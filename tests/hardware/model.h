/* SOLO MODELO: registros simulados para ejecutar el mismo main.c en PC. */
extern uint32_t model_registers[0x30000/4];
extern volatile uint32_t __R30, __R31;
void model_service(void);
void model_step(void);
#undef REG
#define REG(a) model_registers[(a)/4]
#undef M
#define M ((volatile struct mailbox *)&model_registers[0x10000/4])
