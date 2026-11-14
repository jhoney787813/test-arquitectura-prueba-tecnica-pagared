# Conclusiones del candidato: lo que no se ve en el repositorio

Antes de la solución técnica, quiero ser explícito en algo que no cabe en un
diagrama ni en un test unitario: saber SQL, Python, arquitectura o Power BI es
necesario, pero no suficiente para este rol. La diferencia entre un ejercicio
correcto y un compañero de equipo confiable está en cómo se responde cuando
algo falla a las 2:00 a. m., cuando un ticket urgente compite con el trabajo
planeado, cuando el negocio no entiende una decisión técnica y cuando uno
necesita ayuda y debe pedirla sin ego.

En operación, la atención a incidentes no es “apagar el fuego”: es asumir el
incidente, comunicar el estado con honestidad, separar el síntoma de la causa
raíz, corregir los datos si quedaron mal y dejar una prevención que evite que
vuelva a pasar. En esta prueba eso se ve en el análisis de `carga_recaudos_bi`:
no basta con decir “el job está en verde”; hay que leer los logs, los archivos
de control, el historial de Power BI y el tiempo del agente para encontrar que
se cargó una sola parte del archivo y que el tablero refrescó a mitad de la
carga. Esa curiosidad y esa disciplina son las que aplico en incidentes reales.

En tickets de alta prioridad, mi prioridad es el impacto en el negocio, no el
orden de llegada: entender qué se está cayendo, a quién afecta, qué mitigación
inmediata existe y cuándo se comunicará el siguiente avance. Un ticket no
termina cuando el código compila; termina cuando el usuario confirma que puede
trabajar y cuando queda la evidencia para que otro no tenga que empezar de
cero. La documentación de este repositorio —runbook, resultados, decisiones y
aprobaciones— es la misma disciplina que aplico a un ticket.

La comunicación también es parte del trabajo. Traducir “UTC, SCD2 o idempotencia”
a “el reporte llega a las 6:00, no se duplica y el histórico no cambia” es lo
que permite que Laura, Finanzas o un evaluador tomen decisiones. Preguntar
antes de asumir, documentar el supuesto y decir “esto no lo sé todavía, pero
así lo voy a verificar” es más valioso que una respuesta rápida y falsa.

Y sí: pido ayuda. No creo que pedir una segunda opinión, escalar un bloqueo o
reconocer que otro sabe más sea una debilidad; es la forma de no convertir un
problema pequeño en un incidente. En esta prueba corregí el rumbo varias veces:
acepté que el plan monolítico no era la mejor unidad de trabajo, que el `OR`
que propuse para A1 no resolvía el LEFT JOIN y que la estructura inicial no era
la que necesitaba para sustentar el entregable. Esa humildad para corregir es,
para mí, parte del criterio técnico.

Pido al reclutador que, antes de cualquier filtro o prueba técnica, pondere
también estas habilidades: atención a incidentes, resolución de tickets críticos,
comunicación con negocio y técnicos, y disposición a pedir ayuda. El
repositorio demuestra lo que sé construir; esta conclusión explica cómo trabajo
cuando la construcción se encuentra con la realidad.
