"""Build or verify the GES ZIP from a frozen Git commit (Python 3.8+)."""
import argparse
import hashlib
import io
import json
import re
import subprocess
import tarfile
from pathlib import Path, PurePosixPath
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[2]
PREFIXES = ("software/", "tests/", "scripts/entrega/", "hardware/pruebas/",
            "hardware/configuracion/", "hardware/documentacion/fuentes-P2/", "docs/entrega/")
TEXT = {".c", ".h", ".cmd", ".sh", ".ps1", ".py", ".cjs", ".js", ".css", ".html",
        ".md", ".json", ".csv", ".txt", ".dts", ".yml", ".yaml", ".ld"}
REQUIRED = ("software/runtime102/native/firmware.c", "software/runtime102/native/service.c",
            "software/runtime102/native/host.c", "software/runtime102/native/build.sh",
            "software/runtime102/node-web.cjs", "software/runtime102/node-chat.html",
            "software/runtime102/PRIMERAS_TRAMAS_FISICAS.md", "software/matrices102/engine.js",
            "docs/protocolo/TRAMA3_Protocolo_Revision_102.md", "docs/entrega/CHECKLIST_GES.md",
            "docs/entrega/DOCUMENTACION_TECNICA.docx", "docs/entrega/DOCUMENTACION_TECNICA.pdf")
BLOCKED = {".git", "build", "dist", "node_modules", "__pycache__", "credentials", "private",
           "evidencias", "validation-physical", "secrets", ".aws", ".ssh"}
SECRET = re.compile(rb"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----|\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|AKIA[A-Z0-9]{16})\b")
FINAL_REQUIREMENTS = {"chat_bidireccional", "control_limpio", "interferencia_fisica",
                      "tres_medios", "compilacion_ti_arm", "documentacion_final", "integracion_revisada"}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_name(name):
    parts = name.split("/")
    return not any(p in {"", ".", ".."} for p in parts) and not re.search(r"[\\:\x00-\x1f]", name)


def include(path):
    name = path.as_posix()
    if set(part.lower() for part in path.parts) & BLOCKED:
        return False
    if re.search(r"(^|/)(\.env|id_rsa|id_ed25519|credentials|secrets)([./_-]|$)", name, re.I):
        return False
    if name in REQUIRED or name == "README.md" or path.name.startswith(("LICENSE", "COPYING", "NOTICE")):
        return True
    if name in ("hardware/documentacion/Interfaces_T13_T57_Revision102.md",
                "hardware/documentacion/GUIA_DEFINITIVA_T06_T08_P2_BBB-A_BBB-B.md",
                "hardware/documentacion/T08_Auditoria_P2.md",
                "hardware/documentacion/Cierre_T06_2026-11-15.md",
                "docs/planificacion/Informe_Runtime102_Base.md"):
        return True
    if name.startswith("software/matrices102/") and re.search(r"(resultados|ejemplo-corte)", path.name):
        return False
    return name.startswith(PREFIXES) and (path.suffix in TEXT or path.name == "Makefile")


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


def read_source(ref):
    commit = git("rev-parse", "--verify", ref + "^{commit}").decode().strip()
    timestamp = git("show", "-s", "--format=%cI", commit).decode().strip()
    files = {}
    with tarfile.open(fileobj=io.BytesIO(git("archive", "--format=tar", commit))) as archive:
        for entry in archive:
            if not entry.isfile() or not safe_name(entry.name) or not include(PurePosixPath(entry.name)):
                continue
            data = archive.extractfile(entry).read()
            if SECRET.search(data):
                raise ValueError("Possible baked-in credential in " + entry.name)
            files[entry.name] = (data, entry.mode)
    missing = set(REQUIRED) - files.keys()
    if missing:
        raise ValueError("Commit lacks required files: " + ", ".join(sorted(missing)))
    files["software/runtime102/SOURCE_COMMIT"] = ((commit + "\n").encode(), 0o644)
    return commit, timestamp, files


def final_evidence(directory, commit, source):
    release = json.loads((directory / "release.json").read_bytes())
    if release.get("commit") != commit or release.get("schema") != 1:
        raise ValueError("Release evidence must refer to the frozen commit")
    requirements = release.get("requirements", {})
    if set(requirements) != FINAL_REQUIREMENTS or any(value != "CUMPLE" for value in requirements.values()):
        raise ValueError("Physical and integration acceptance is incomplete")
    files = {}
    base = directory.resolve()
    for name, expected in release["files"].items():
        if not safe_name(name) or name == "release.json":
            raise ValueError("Invalid evidence path: " + name)
        file = (base / name).resolve(strict=True)
        if base not in file.parents or not file.is_file():
            raise ValueError("Evidence path outside approved directory: " + name)
        data = file.read_bytes()
        if digest(data) != expected or SECRET.search(data):
            raise ValueError("Evidence hash or content invalid: " + name)
        files[name] = (data, 0o644)
    for key, scope in (("control_report", "bidirectional-delivery-and-cleanup"), ("interference_report", "crc-nack-retry")):
        report_name = release[key]
        report = json.loads(files[report_name][0])
        if report.get("scope") != scope or report.get("status") != "PASS" or report.get("origin") != "hardware":
            raise ValueError("Physical report required: " + report_name)
        if key == "control_report" and any(report[node]["rejections"] or
                                           report[node]["retries"] for node in ("A", "B")):
            raise ValueError("Control trial includes rejected frames or retries")
        if key == "interference_report" and (report.get("physical_status") != "CUMPLE" or report.get("commit") != commit):
            raise ValueError("Interference must pass on the frozen commit")
        for name, expected in report["evaluator_sources"].items():
            if digest(source["software/runtime102/" + name][0]) != expected:
                raise ValueError("Report used an evaluator outside the frozen commit")
        reports = release["report_inputs"][key]
        if len(reports) != 3 or len(report["inputs"]) != 3:
            raise ValueError("Include the manifest and original A/B logs for each report")
        for name, item in zip(reports, report["inputs"]):
            if digest(files[name][0]) != item["sha256"]:
                raise ValueError("Report input hash mismatch: " + name)
        for name in reports[1:]:
            launch = json.loads(files[name][0].splitlines()[0])
            if launch.get("commit") != commit or launch.get("origin") != "hardware":
                raise ValueError("Original logs must come from the frozen hardware build")
        if key == "interference_report":
            manifest_dir = PurePosixPath(reports[0]).parent
            for entry in report["media"]:
                if digest(files[(manifest_dir / entry["path"]).as_posix()][0]) != entry["sha256"]:
                    raise ValueError("Physical attachment hash mismatch")
    for name in (release["nominal_report"], release["build_record"], release["integration_record"]):
        if not files[name][0].strip():
            raise ValueError("Empty release evidence: " + name)
    files["release.json"] = ((directory / "release.json").read_bytes(), 0o644)
    return {"evidencias/" + name: value for name, value in files.items()}, requirements


def verify(archive):
    with ZipFile(archive) as zip_file:
        names = zip_file.namelist()
        if len(names) != len(set(names)) or not all(safe_name(name) for name in names):
            raise ValueError("Unsafe or duplicate ZIP member")
        if zip_file.testzip() is not None:
            raise ValueError("ZIP CRC mismatch")
        manifest = json.loads(zip_file.read("MANIFIESTO.json"))
        files = manifest["sha256"]
        if set(files) | {"SHA256SUMS", "MANIFIESTO.json"} != set(names) or not set(REQUIRED) <= files.keys():
            raise ValueError("Manifest and ZIP entries differ")
        sums = "".join(f"{value}  {name}\n" for name, value in sorted(files.items()))
        sums += f"{digest(zip_file.read('MANIFIESTO.json'))}  MANIFIESTO.json\n"
        if sums.encode() != zip_file.read("SHA256SUMS"):
            raise ValueError("SHA256SUMS and manifest differ")
        for name, expected in files.items():
            if digest(zip_file.read(name)) != expected:
                raise ValueError("SHA-256 mismatch: " + name)
        if zip_file.read("software/runtime102/SOURCE_COMMIT").decode().strip() != manifest["commit"]:
            raise ValueError("Source commit mismatch")
    return manifest


def build(args):
    commit, timestamp, files = read_source(args.ref)
    requirements = {name: "PENDIENTE" for name in sorted(FINAL_REQUIREMENTS)}
    if args.mode == "final":
        if args.evidence is None:
            raise ValueError("The final ZIP requires reviewed physical evidence (--evidence)")
        evidence, requirements = final_evidence(args.evidence, commit, files)
        files.update(evidence)
    manifest = {
        "schema": 1, "state": "PREPARADO" if args.mode == "provisional" else "FINAL",
        "commit": commit, "commit_date": timestamp, "protocol_revision": 102, "abi": 4,
        "firmware": "runtime102-pru0.out, compiled from the frozen ABI4 sources",
        "host": "runtime102-host, compiled locally for ARM on each BBB",
        "dependencies": ["Node.js >=16.20.2 (built-in modules)", "Python 3", "GCC", "TI clpru",
                         "GNU Bash", "Linux PRU remoteproc, PWM, I2C and pinmux"],
        "build_command": "bash software/runtime102/native/build.sh",
        "operation": "docs/entrega/CHECKLIST_GES.md",
        "requirements": requirements,
        "sha256": {name: digest(data) for name, (data, _) in sorted(files.items())},
    }
    files["MANIFIESTO.json"] = ((json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode(), 0o644)
    sums = "".join(f"{value}  {name}\n" for name, value in sorted(manifest["sha256"].items()))
    sums += f"{digest(files['MANIFIESTO.json'][0])}  MANIFIESTO.json\n"
    files["SHA256SUMS"] = (sums.encode(), 0o644)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as target:
        try:
            with ZipFile(target, "w") as archive:
                for name, (data, mode) in sorted(files.items()):
                    info = ZipInfo(name)
                    info.create_system = 3
                    info.external_attr = (0o100000 | mode) << 16
                    archive.writestr(info, data, compress_type=ZIP_DEFLATED, compresslevel=9)
            target.flush()
            verify(args.output)
        except BaseException:
            target.close()
            args.output.unlink()
            raise
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    make = commands.add_parser("build")
    make.add_argument("mode", choices=["provisional", "final"])
    make.add_argument("output", type=Path)
    make.add_argument("--ref", required=True, help="Git commit or ref to freeze")
    make.add_argument("--evidence", type=Path)
    check = commands.add_parser("verify")
    check.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        result = build(args) if args.command == "build" else verify(args.output)
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as error:
        parser.exit(1, str(error) + "\n")
    print(result["state"], result["commit"], len(result["sha256"]), args.output)
    print(digest(args.output.read_bytes()), args.output.name)


if __name__ == "__main__":
    main()
