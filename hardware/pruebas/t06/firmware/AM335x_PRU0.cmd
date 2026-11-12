/* PRU0: 8 KiB IRAM, 8 KiB DRAM; mailbox fuera de las secciones enlazadas. */
-cr
--entry_point=_c_int00
--stack_size=0x100
--heap_size=0x100
MEMORY {
 PAGE 0: PRU_IMEM: origin=0x00000000 length=0x00002000
 PAGE 1: PRU_DMEM: origin=0x00000000 length=0x00002000
}
SECTIONS {
 .text > PRU_IMEM, PAGE 0
 .stack > PRU_DMEM, PAGE 1
 .bss > PRU_DMEM, PAGE 1
 .data > PRU_DMEM, PAGE 1
 .cinit > PRU_DMEM, PAGE 1
 .const > PRU_DMEM, PAGE 1
 .rodata > PRU_DMEM, PAGE 1
 .sysmem > PRU_DMEM, PAGE 1
 .resource_table > PRU_DMEM, PAGE 1
}
