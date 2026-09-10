**Desarrollo de Backend · ICINF1108**

# **Proyecto grupal: diseño e implementación** **de una API backend (15%)**

## *Guía de trabajo, ruta de avance y criterios de evaluación*

| Dato | Definición obligatoria |
| ----- | ----- |
| **Curso** | Desarrollo de Backend (ICINF1108). |
| **Integrantes** | Grupos definidos previamente para cada sección. |
| **Producto** | API REST funcional, repositorio Git y presentación de apoyo. |
| **Tecnología** | Ej.: Python, FastAPI, Pydantic y Uvicorn, u otras tecnologías autorizadas. |
| **Almacenamiento** | En memoria mediante listas o diccionarios. No se exige base de datos en esta entrega. |
| **Evaluación** | Código: 40%. Presentación y defensa: 60%. |
| **Entrega** | semana 6: 14 y 16 de septiembre a las \[HORA\], mediante \[PLATAFORMA\]. |
| **Defensa** | semana 6:  14 y 16 de septiembre. Duración: 10 minutos de presentación y 5 minutos de preguntas. |

**Resultado esperado:** Durante la defensa, el proyecto deberá ejecutarse localmente. El grupo abrirá la documentación Swagger/OpenAPI o una colección de pruebas en Postman, Thunder Client o una herramienta equivalente. Desde allí deberá probar los endpoints y comprobar que la API responde según el contrato definido por el grupo.

**Fuera de alcance:** no se solicita interfaz gráfica ni aplicación Frontend. Tampoco se exige autenticación, base de datos o despliegue en Internet para esta entrega.

# 

# **1\. Propósito del proyecto**

Cada grupo debe proponer una problemática concreta y construir una API REST que permita ejecutar acciones relacionadas con ella. La propuesta debe precisar quién experimenta el problema, qué necesita hacer y qué información administrará el backend.

**Ejemplo:** «Gestionar una biblioteca» es demasiado general. Una formulación concreta sería: «Las personas encargadas de una biblioteca universitaria registran préstamos en planillas separadas y no pueden saber qué ejemplares están disponibles ni cuáles presentan atraso».

# **2\. Organización obligatoria del grupo**

Los grupos estarán conformados por 4 o 5 estudiantes, de acuerdo con la **distribución establecida para cada sección**. Todos los grupos deberán desarrollar los mismos requisitos técnicos y entregar los mismos productos, independientemente de la cantidad de integrantes.

Cada grupo deberá designar a un jefe o jefa de grupo, responsable de coordinar el trabajo, realizar seguimiento de los avances y mantener la comunicación con el equipo docente. Esta responsabilidad de coordinación no exime a la persona de participar en el desarrollo técnico del proyecto.

Para organizar el trabajo, cada grupo deberá cubrir las siguientes cinco áreas de responsabilidad:

| Área de responsabilidad | Responsabilidad principal |
| ----- | ----- |
| **Coordinación y seguimiento** | Organización del backlog, seguimiento de tareas, reuniones, control de avances e integración de entregables. |
| **Dominio y datos** | Modelado de entidades, relaciones, DTO, validaciones y coherencia del modelo del dominio. |
| **API y lógica de negocio** | Implementación de endpoints, servicios, reglas de negocio y manejo de errores. |
| **Calidad y pruebas** | Verificación funcional de endpoints, casos exitosos y de error, colección de pruebas y revisión del funcionamiento general. |
| **Documentación e integración** | Swagger/OpenAPI, README, documentación técnica y revisión de la integración de los distintos componentes del proyecto. |

**Distribución de responsabilidades:** En los grupos de cinco integrantes, cada estudiante podrá asumir como responsabilidad principal una de las cinco áreas. En los grupos de cuatro integrantes, una persona deberá asumir dos áreas compatibles. La distribución deberá quedar registrada por el grupo antes de comenzar el desarrollo.

**Nota:** Las responsabilidades indican quién realiza el seguimiento principal de cada área, pero no representan una división exclusiva del proyecto. Todos los integrantes deberán comprender el funcionamiento completo de la API y participar activamente en su desarrollo, pruebas e integración.

**Para grupos de cuatro integrantes** se recomienda combinar **Coordinación y seguimiento con Documentación e integración**, aunque el grupo podrá realizar otra distribución si justifica que la carga de trabajo permanece equilibrada.

**Ejemplo para grupos de 4 estudiantes:**

| Estudiante | Responsabilidad principal |
| ----- | ----- |
| **A** | Coordinación \+ documentación e integración |
| **B** | Dominio y datos |
| **C** | API y lógica de negocio |
| **D** | Calidad y pruebas |

# **3\. Ruta de trabajo por hitos**

La siguiente tabla muestra un ejemplo de cómo organizar el desarrollo del proyecto mediante hitos. Los hitos presentados no deben copiarse necesariamente de forma textual.

Cada grupo deberá definir su propia ruta de trabajo considerando las características de su proyecto y los requisitos de esta guía. Para hacerlo:

1. Identifiquen las principales etapas necesarias para desarrollar su proyecto.  
2. Ordenen las etapas desde el trabajo inicial hasta la versión que presentarán.  
3. Definan qué tareas principales realizarán en cada hito.  
4. Distribuyan las tareas entre los integrantes y actualicen la planificación cuando sea necesario.

La ruta debe ser simple, comprensible y permitir observar cómo el proyecto avanzará progresivamente.

| Hito | Tareas principales |
| ----- | ----- |
| **Hito 1** | Definir la problemática, confirmar el grupo, crear el repositorio, asignar responsabilidades y redactar el alcance. |
| **Hito 2** | Modelar las cuatro entidades e implementar las primeras rutas CRUD con almacenamiento en memoria. |
| **Hito 3** | Aplicar métodos HTTP, códigos de estado, headers necesarios, validaciones y un formato uniforme de errores. |
| **Hito 4** | Completar el contrato REST, los DTO, la documentación, el filtrado, el ordenamiento y la paginación. |
| **Hito …** | …. |
| **Hito N** | …. |

# **4\. Requisitos de la problemática**

La presentación debe responder P1 a P7. Conviene completar una pregunta a la vez y usar ejemplos concretos del proyecto.

| Pregunta | Tema | Respuesta mínima |
| :---: | ----- | ----- |
| **P1** | ¿Qué situación concreta ocurre actualmente? | Describa un hecho observable, sin formular todavía la solución. |
| **P2** | ¿Quiénes experimentan el problema? | Identifique al menos dos tipos de usuario o actor. |
| **P3** | ¿Qué consecuencia produce el problema? | Indique al menos dos consecuencias observables. |
| **P4** | ¿Qué información administrará el sistema? | Precise qué se registrará, consultará, modificará o eliminará. |
| **P5** | ¿Qué acciones debe permitir la API? | Escriba al menos ocho requisitos con la forma «El sistema debe permitir ... |
| **P6** | ¿Qué no resolverá esta primera versión? | Indique al menos tres exclusiones de alcance. |
| **P7** | ¿Cómo se sabrá que la solución funciona? | Defina al menos cinco criterios de aceptación comprobables. |

# **5\. Requisitos técnicos obligatorios**

## **5.1 Modelo del dominio (Cada ítem es obligatorio)**

* El modelo debe contener al menos cuatro entidades principales.   
* Cada entidad tendrá un identificador único y, además del identificador, al menos cuatro atributos útiles para el problema.   
* Entre dos entidades deberá existir al menos una relación uno-a-muchos.  
* El grupo presentará un diagrama de clases legible y definirá al menos tres reglas de negocio que expresen decisiones o restricciones del dominio. **Nota:** Una regla de negocio no es lo mismo que una validación de tipo o formato.

**Ejemplo:** «Una reserva no puede finalizar antes de comenzar» es una regla de negocio. «El nombre es texto» corresponde a una validación de datos.

## **5.2 Contrato de la API (Cada ítem es obligatorio)**

* La API debe implementar al menos doce endpoints funcionales. Una entidad tendrá CRUD completo: crear, listar, obtener por ID, actualizar y eliminar.  
* Las URI usarán sustantivos plurales, por ejemplo /productos y /productos/{producto\_id}. Se utilizará GET para consultar, POST para crear, PUT o PATCH para actualizar y DELETE para eliminar.  
* Cuando los campos de entrada y salida sean diferentes, se definirán DTO separados. Cada endpoint deberá documentar su resumen, descripción, parámetros, ejemplos de entrada y salida y respuestas posibles. Swagger/OpenAPI es la opción preferente; si el framework no lo genera, se aceptará una colección equivalente en Postman, Thunder Client u otra herramienta, siempre que el README conserve la tabla completa del contrato.

## **5.3 Validación de datos**

La API debe rechazar datos inválidos antes de ejecutar la operación. Se requieren al menos seis validaciones distribuidas entre las entidades; cada tipo de la tabla debe aparecer al menos una vez.

| Tipo mínimo | Qué debe comprobar |
| ----- | ----- |
| **Longitud** | Mínimo o máximo de caracteres. |
| **Numérica** | Mayor que, mayor o igual que, menor que o rango permitido. |
| **Valores permitidos** | Conjunto controlado, por ejemplo un estado definido con Enum. |
| **Formato** | Correo electrónico, fecha u otro formato verificable. |
| **Existencia relacionada** | Comprobación de que el recurso relacionado existe. |
| **Regla de negocio** | Validación vinculada a una decisión o restricción del dominio. |

## 

## 

## **5.4 Respuestas y errores HTTP**

La API utilizará los siguientes códigos cuando corresponda. El criterio no se basa en el color de la respuesta, sino en el código, el contenido y la situación que representa.

| Código | Definición obligatoria |
| ----- | ----- |
| **200 OK** | Consulta, actualización o eliminación correcta cuando se devuelve contenido. |
| **201 Created** | Recurso creado correctamente. |
| **204 No Content** | Eliminación correcta cuando no se devuelve contenido. |
| **400 Bad Request** | La solicitud es comprensible, pero viola una regla de negocio. |
| **404 Not Found** | El recurso solicitado no existe. |
| **409 Conflict** | La operación entra en conflicto con el estado actual, por ejemplo un registro duplicado. |
| **422 Unprocessable Entity** | Los datos no cumplen el esquema o las validaciones declaradas. |

Todos los errores controlados por el grupo deben conservar la misma estructura JSON:

{  
  "error": {  
    "code": "RESOURCE\_NOT\_FOUND",  
    "message": "No existe un producto con el ID solicitado",  
    "details": \[\]  
  }  
}

## **5.5 Filtrado, ordenamiento y paginación**

Un mismo endpoint GET que devuelve una colección debe permitir filtrado, ordenamiento y paginación. No basta con implementar solo una o dos de las operaciones.

**Ejemplo de solicitud:** GET /productos?categoria=electronica\&ordenar\_por=precio\&direccion=asc\&pagina=2\&limite=20

| Operación | Definición obligatoria |
| ----- | ----- |
| **Filtrado** | *categoria* conserva únicamente los elementos cuya categoría coincide con el valor recibido. |
| **Ordenamiento** | *ordenar\_por* selecciona el atributo y *direccion* acepta solamente *asc* o *desc*. |
| **Paginación** | *pagina* comienza en 1\. *limite* indica cuántos elementos se devuelven y acepta valores entre 1 y 100\. |
| **Orden obligatorio** | Primero filtrar, después ordenar y finalmente paginar. |

La respuesta debe usar esta estructura general:

{  
  "items": \[\],  
  "total": 85,  
  "pagina": 2,  
  "limite": 20,  
  "total\_paginas": 5  
}

## 

## **5.6 Arquitectura y organización del código**

El proyecto debe separar responsabilidades. Como mínimo, deberá utilizar la siguiente organización o una estructura equivalente que mantenga las mismas responsabilidades:

app/  
    main.py                 \# crea y configura la aplicación  
    routers/                \# recibe solicitudes HTTP  
    schemas/                \# DTO y validaciones  
    domain/                 \# entidades y reglas del dominio  
    services/               \# casos de uso y reglas de negocio  
    repositories/           \# almacenamiento en memoria  
tests\_manual/               \# colección Postman, Thunder Client o archivo .http  
README.md  
requirements.txt o pyproject.toml

**Regla de separación:** Una ruta no debe contener directamente toda la lógica del problema. La ruta recibe los datos, coordina la respuesta HTTP y delega la operación al servicio correspondiente.

## **5.7 Ejecución**

El proyecto debe ejecutarse localmente siguiendo únicamente las instrucciones del README. El comando recomendado debe aparecer de forma literal y funcionar desde una copia limpia del repositorio.

No se incluirán contraseñas, tokens ni archivos .env con credenciales reales.

# **6\. Entregables y nombres de archivos**

| Entregable | Definición obligatoria |
| ----- | ----- |
| **E1. Repositorio** | Repositorio Git accesible al docente. Nombre: backend-2026-grupo-XX. |
| **E2. Pruebas manuales** | Colección Postman o Thunder Client exportada, o archivo .http. Debe permitir repetir las solicitudes principales. |
| **E3. Contrato de la API** | Swagger/OpenAPI accesible desde la ruta provista por el framework o documentación equivalente, junto con la tabla del contrato en el README. |

# **7\. Requisitos del repositorio Git**

**Contribución individual:** cada integrante debe realizar al menos cinco commits propios y significativos, trabajar en al menos una rama distinta de main y crear al menos un pull request.

**Mensajes de commit:** deben indicar la acción realizada. Se acepta, por ejemplo, «Agrega validación de stock en Producto». No se consideran evidencia mensajes genéricos como «cambios», «avance», «fix» o equivalentes sin descripción.

**README.md:** debe incluir instalación, ejecución, estructura del proyecto, integrantes, responsabilidades, contrato de endpoints y acceso a Swagger/OpenAPI o a la herramienta equivalente utilizada para la demostración.

# **8\. Presentación y defensa**

Al inicio de la defensa, el docente seleccionará al azar a una persona del grupo para realizar la presentación completa. El resto del equipo intervendrá después, durante las preguntas. Todos deben poder explicar cualquier parte del proyecto.

| Aspecto | Definición obligatoria |
| ----- | ----- |
| **Duración** | 10 minutos de presentación y demostración, seguidos de 5 minutos de preguntas. |
| **Demostración** | La API se ejecuta en vivo y se prueban al menos cuatro endpoints: dos casos exitosos, un error y la colección con filtro, orden y paginación. |
| **Herramienta** | Swagger/OpenAPI o una colección equivalente en Postman, Thunder Client u otra herramienta de prueba. |
| **Apoyo visual** | Máximo 15 diapositivas. La demostración de la API no cuenta como diapositiva. |
| **Ritmo y secuencia** | Mantener un ritmo estable, anunciar los cambios de sección y presentar una idea principal por diapositiva. |
| **Accesibilidad visual** | El contenido debe ser legible y comprensible sin depender solo del color. Los estados, categorías y relaciones deben incluir texto, símbolos, patrones o etiquetas, además de contraste suficiente. |
| **Preguntas** | Cualquier integrante puede responder preguntas sobre cualquier parte del código. |

Orden obligatorio de la presentación:

1. Problema, usuarios y alcance.  
2. Modelo del dominio y reglas principales.  
3. Contrato de la API y arquitectura.  
4. Demostración funcional.  
5. Decisiones, limitaciones y mejoras futuras.

# **9\. Lista de verificación antes de entregar**

Antes de realizar la entrega, el grupo debe revisar los siguientes puntos y comprobar que cada uno se cumple en la versión final del proyecto. Si detectan un elemento pendiente, deben resolverlo antes de entregar o informar al equipo docente si existe alguna dificultad.

* Las cuatro o cinco responsabilidades están asignadas y registradas.  
* El repositorio se puede clonar y ejecutar siguiendo únicamente el README.  
* La documentación o colección de prueba permite identificar y ejecutar al menos doce endpoints.  
* Existe CRUD completo para al menos una entidad.  
* Existen cuatro entidades, cada una con ID y cuatro atributos útiles, y una relación uno-a-muchos.  
* Existen al menos seis validaciones y tres reglas de negocio comprobables.  
* Un mismo GET implementa filtrado, ordenamiento y paginación en el orden exigido.  
* La API utiliza almacenamiento en memoria y no contiene credenciales reales.  
* El README contiene instalación, ejecución, estructura, integrantes, responsabilidades y contrato de endpoints.  
* La colección de pruebas puede importarse o ejecutarse.  
* La contribución Git de cada integrante es visible mediante commits, ramas y pull requests.  
* La presentación usa máximo 15 diapositivas y no depende solo del color para comunicar información.  
* La presentación dura 10 minutos y puede ser realizada completamente por cualquier integrante elegido al azar; los demás intervienen después, durante las preguntas.

**Recomendación:** Realicen una defensa de ensayo completa con cronómetro. Una persona distinta debe ejecutar la API siguiendo el README y repetir los cuatro casos de la demostración sin recibir instrucciones adicionales.

# **Rúbrica 1\. Código (40% de la calificación final)**

| Criterio | Completo(3 pts) | Parcial alto(2 pts) | Parcial bajo(1 pt) | No cumple(0 pts) |
| ----- | ----- | ----- | ----- | ----- |
| **1\. Ejecución y endpoints** | La API inicia con el comando indicado y los 12 o más endpoints pueden ejecutarse sin errores no controlados. | La API inicia; uno o dos endpoints presentan un error menor o requieren una corrección puntual. | La API inicia, pero funcionan solo entre 8 y 11 endpoints o requiere ayuda para ejecutarse. | La API no inicia o funcionan menos de 8 endpoints. |
| **2\. Modelo del dominio** | El código contiene al menos 4 entidades, cada una con ID y 4 atributos útiles, y una relación 1:N funcional. | Cumple lo anterior, pero existe una inconsistencia menor entre una entidad, atributo o relación. | Falta una entidad, varios atributos requeridos o la relación 1:N no funciona. | No existe un modelo de dominio identificable en el código. |
| **3\. Contrato REST y documentación** | URI, métodos, DTO, parámetros, respuestas y documentación son coherentes en los 12 o más endpoints. Swagger/OpenAPI o la herramienta equivalente puede abrirse y utilizarse. | Hasta dos endpoints presentan una inconsistencia de método, URI, DTO, respuesta o documentación. | Entre 3 y 5 endpoints presentan inconsistencias, o la documentación o colección de prueba está incompleta. | Más de 5 endpoints incumplen el contrato o no existe documentación o medio de prueba disponible. |
| **4\. CRUD y funcionamiento** | Una entidad tiene CRUD completo y las operaciones mantienen datos coherentes durante toda la ejecución. | El CRUD está completo, pero una operación presenta un error menor reproducible. | El CRUD está incompleto o dos operaciones no producen el resultado definido. | No existe un CRUD funcional. |
| **5\. Validaciones y reglas** | Implementa 6 o más validaciones y 3 reglas de negocio; todas rechazan o permiten los casos definidos. | Falta o falla una validación o una regla de negocio. | Implementa solo 3 a 5 validaciones o solo 1 a 2 reglas de negocio funcionales. | No implementa validaciones ni reglas de negocio comprobables. |
| **6\. Respuestas y errores HTTP** | Usa correctamente los estados requeridos y todos los errores controlados mantienen la estructura JSON definida. | Un caso utiliza un estado incorrecto o no conserva la estructura de error. | Varios casos usan estados incorrectos o la estructura de error cambia entre endpoints. | No existe manejo controlado de errores. |
| **7\. Filtro, orden y paginación** | Un mismo GET filtra, ordena y pagina en ese orden; valida parámetros y devuelve todos los metadatos exigidos. | Las 3 operaciones funcionan, pero falta una validación o un metadato. | Funcionan solamente una o dos de las tres operaciones. | No implementa esta funcionalidad. |
| **8\. Arquitectura y calidad** | Separa routers, schemas, domain, services y repositories; la lógica no está concentrada en las rutas. | La separación es mayormente correcta, con una responsabilidad ubicada en una capa inadecuada. | Existen carpetas, pero la mayor parte de la lógica permanece en main o routers. | El código es monolítico, no legible o no permite identificar responsabilidades. |

**Puntaje obtenido: \_\_\_\_\_\_ / 24**

**Observación específica y evidencia:** \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

# **Rúbrica 2\. Presentación y defensa (60% de la calificación final)**

| Criterio | Completo(3 pts) | Parcial alto(2 pts) | Parcial bajo(1 pt) | No cumple(0 pts) |
| ----- | ----- | ----- | ----- | ----- |
| **1\. Problemática y alcance** | Explica P1-P7: situación, actores, consecuencias, información, acciones, exclusiones y criterios de aceptación concretos. | Explica P1-P7, pero uno de los elementos es general o no comprobable. | Omite dos o tres elementos o describe un tema sin precisar el problema. | No permite comprender qué problema resuelve el proyecto. |
| **2\. Dominio y reglas** | Explica 4 entidades, sus atributos, la relación 1:N, 6 validaciones y 3 reglas de negocio con ejemplos. | Presenta todos los elementos, pero uno no coincide completamente con el proyecto. | Omite una entidad, la relación, varias validaciones o reglas de negocio. | No presenta un modelo de dominio comprensible. |
| **3\. Contrato y arquitectura** | Explica endpoints, DTO, estados, errores y el flujo entre routers, services y repositories con ejemplos del proyecto. | Explica los componentes, pero omite una relación o una justificación. | Solo enumera componentes o endpoints sin explicar cómo se relacionan. | No puede explicar el contrato ni la arquitectura. |
| **4\. Demostración funcional** | Ejecuta 4 o más endpoints en Swagger/OpenAPI o herramienta equivalente: dos casos exitosos, un error y la colección con filtro, orden y paginación. | La demostración funciona, pero falta uno de los cuatro casos exigidos. | Solo demuestra dos casos o necesita reiniciar o corregir la API durante la exposición. | No realiza una demostración funcional. |
| **5\. Decisiones y limitaciones** | Justifica modelado, endpoints, validaciones y arquitectura; además identifica una limitación y dos mejoras futuras. | Justifica la mayoría de las decisiones, pero una queda sin fundamento concreto. | Describe decisiones como preferencias y no las relaciona con el problema. | No explica decisiones técnicas ni limitaciones. |
| **6\. Presentación sorteada** | El integrante elegido al azar realiza la presentación completa sin intervención de sus compañeros. | Realiza toda la presentación, pero recibe una intervención breve antes de terminar. | Otro integrante debe continuar una parte sustantiva de la presentación. | No presenta la persona seleccionada o el grupo distribuye la exposición. |
| **7\. Preguntas y defensa** | Después de la presentación, las respuestas son precisas y los integrantes pueden explicar cualquier parte del proyecto. | La mayoría de las respuestas es correcta; una requiere un complemento menor. | Varias respuestas son incompletas o dependen reiteradamente de una sola persona. | El grupo no demuestra comprensión del proyecto. |
| **8\. Claridad, apoyo y tiempo** | Sigue el orden exigido, utiliza máximo 15 diapositivas, lenguaje claro, ritmo estable y apoyo legible que no depende solo del color; finaliza dentro de los 10 minutos. | Presenta una desviación menor de orden, cantidad de diapositivas, legibilidad o tiempo de hasta 1 minuto. | Dura menos de 7 o más de 12 minutos, o la secuencia o el apoyo visual dificultan la comprensión o dependen solo del color. | La presentación no permite evaluar el proyecto. |

**Puntaje obtenido: \_\_\_\_\_\_ / 24**

**Observación específica y evidencia:** \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

## **Cálculo de la calificación final**

La calificación final se obtiene mediante la fórmula (Nota Rúbrica 1 × 0,40) \+ (Nota Rúbrica 2 × 0,60), donde cada rúbrica se convierte previamente a nota mediante Nota \= 1 \+ (puntaje obtenido / 24).