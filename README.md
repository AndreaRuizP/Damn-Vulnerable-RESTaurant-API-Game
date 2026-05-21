# Proyecto Final de Curso: Análisis y Mitigación de Vulnerabilidades
## 1. Selección del Sistema Vulnerable

* **Nombre del Sistema:** Damn Vulnerable RESTaurant API Game
* **Tipo de Aplicación:** API RESTful (Backend) construida con Python (FastAPI) y PostgreSQL.
* **Descripción General y Propósito:** Es una plataforma de entrenamiento desarrollada de forma intencionalmente insegura. Simula el sistema de gestión de un restaurante (creación de platos, órdenes, perfiles de usuario y asignación de roles como Chef o Empleado). Su propósito principal es servir como un entorno controlado ("caja de arena") para que ingenieros de software e investigadores de ciberseguridad puedan detectar, explotar y, posteriormente, mitigar vulnerabilidades basadas en el OWASP API Security Top 10.

## Contexto del Problema
Las interfaces de programación de aplicaciones (APIs) se han convertido en el eje central de los sistemas de software modernos, permitiendo la comunicación entre componentes, la integración con terceros y la exposición de funcionalidades de negocio a través de la red. Sin embargo, esta centralidad las convierte también en uno de los vectores de ataque más explotados en la actualidad.
En el sector de restaurantes, la digitalización de operaciones críticas como el registro de usuarios, la autenticación, la administración del menú y el control de roles internos a través de APIs web expone a las organizaciones a riesgos significativos si dichas interfaces no son diseñadas, implementadas y configuradas siguiendo principios de seguridad sólidos.
El proyecto Damn Vulnerable RESTaurant API, construido con Python FastAPI y PostgreSQL, representa un entorno deliberadamente inseguro que reproduce vulnerabilidades reales identificadas en sistemas productivos del sector. Este sistema constituye el objeto de análisis del presente trabajo, cuyo propósito es identificar y relacionar sus fallas de seguridad con el estándar OWASP API Security Top 10 (2023), la referencia más actualizada y reconocida a nivel mundial para la evaluación de riesgos en APIs.
El OWASP API Security Top 10 (2023) identifica las diez categorías de riesgo más críticas en APIs, entre las que se destacan: la autorización rota a nivel de objeto (API1), la autenticación deficiente (API2), la autorización rota a nivel de propiedades de objeto (API3), el consumo irrestricto de recursos (API4), la autorización rota a nivel de función (API5), el acceso irrestricto a flujos de negocio sensibles (API6), la falsificación de solicitudes del lado del servidor (API7), la mala configuración de seguridad (API8), la gestión inadecuada del inventario de APIs (API9) y el consumo inseguro de APIs de terceros (API10).
La explotación de cualquiera de estas vulnerabilidades en el contexto de la plataforma analizada puede comprometer la confidencialidad de datos de usuarios y del negocio, la integridad de las operaciones (como la manipulación del menú o la escalada de privilegios), y la disponibilidad del servicio, con consecuencias directas sobre la confianza de los clientes y la responsabilidad legal de la organización.
El equipo de ingeniería de software tiene como misión realizar un análisis técnico sistemático de las vulnerabilidades presentes en el sistema, clasificarlas según el estándar mencionado y proponer soluciones concretas que reduzcan el nivel de riesgo a uno aceptable para la operación segura del negocio.

## Análisis de Vulnerabilidades Encontradas
A continuación, se detalla el análisis y corrección de seis (6) vulnerabilidades críticas halladas en el sistema, correspondientes a los niveles Level 0 al Level 5 del juego, cumpliendo con las rúbricas de evaluación.

### Vulnerabilidad 1: Level 0 — Exposición de Información Sensible (owasp-1.py)

**2. Identificación y caracterización**

* **Descripción:** El endpoint de estado (/healthcheck) inyectaba manualmente una cabecera HTTP (X-Powered-By) revelando que el servidor corría con "Python 3.10 y FastAPI ^0.103.0".
* **Riesgo de seguridad asociado:** Medio. Facilita la fase de reconocimiento (enumeración pasiva) para un atacante.
* **Categoría OWASP:** API8:2023 — Security Misconfiguration / Information Exposure.
* **Impacto potencial:** Si se descubre un fallo de día cero (0-day) en esa versión específica de FastAPI, los atacantes pueden buscar en Internet servidores que expongan esa cabecera y atacarlos con exploits automatizados de forma masiva.

**3. Análisis técnico y ético** 

* **Origen de la vulnerabilidad:** Implementación. El desarrollador añadió metadatos técnicos en el código productivo.
* **Responsabilidad Ética:** Un ingeniero de software debe guiarse por el principio de mínima divulgación. Exponer información interna por vanidad tecnológica o descuidos de depuración compromete la infraestructura de la empresa.

**4. Propuesta y aplicación de mitigación**

* **Refactorización:** Se eliminó la inyección de las cabeceras response.headers["X-Powered-By"].
* **Controles aplicados:** Sanitización de respuestas HTTP.
* **Justificación:** Limitar los metadatos incrementa el costo y el esfuerzo de un atacante para descubrir qué vulnerabilidades afectan a la infraestructura (Security through obscurity, que aunque no es defensa absoluta, es una buena práctica de hardening).

**5. Validación de la solución**

* **Verificación:** El endpoint ahora retorna exclusivamente el payload {"ok": True}. Una inspección con herramientas como curl -I evidencia la ausencia de la cabecera X-Powered-By, validando la corrección.


### Vulnerabilidad 2: Level 1 — Falta de Autorización a Nivel de Función / BFLA (owasp-2.py)

**2. Identificación y caracterización**

* **Descripción:** El endpoint DELETE /menu/{item_id} no contaba con ningún verificador de roles. Cualquier usuario autenticado, incluidos aquellos con el rol básico de Customer, podía eliminar platos del menú del restaurante sin ninguna restricción.
Riesgo de seguridad asociado: Alto. Riesgo crítico a la integridad operativa del negocio.
* **Categoría OWASP:** API5:2023 — Broken Function Level Authorization (BFLA).
* **Impacto potencial:** Cualquier cliente registrado podría vaciar completamente el menú del restaurante, paralizando las operaciones y generando pérdidas económicas directas. La autenticación (verificar quién eres) estaba implementada, pero la autorización (verificar qué puedes hacer) era inexistente.

**3. Análisis técnico y ético**

* **Origen de la vulnerabilidad:** Diseño de seguridad incompleto (Autenticación sin Autorización).
* **Responsabilidad Ética:** El ingeniero es responsable de diferenciar entre "saber quién eres" (autenticación) y "saber qué puedes hacer" (autorización). Omitir esta validación es negligencia técnica que expone al negocio a sabotaje deliberado por parte de usuarios con acceso legítimo al sistema.

**4. Propuesta y aplicación de mitigación**

* **Refactorización:** Se inyectó un middleware de dependencias auth=Depends(RolesBasedAuthChecker([UserRole.EMPLOYEE, UserRole.CHEF])) en la definición del endpoint DELETE /menu/{item_id}.
* **Controles aplicados:** Control de Acceso Basado en Roles (RBAC).
* **Justificación:** Centraliza la lógica de permisos en el nivel de enrutamiento. FastAPI interceptará la solicitud y si el JWT del usuario no contiene el rol de Empleado o Chef, rechazará la petición automáticamente antes de ejecutar cualquier lógica de negocio.

**5. Validación de la solución**

* **Verificación:** Si un usuario con rol Customer realiza un DELETE /menu/1, el sistema retorna un error HTTP 403 Forbidden. Únicamente cuentas con rol Employee o Chef pueden eliminar platos. La vulnerabilidad queda eliminada.


### Vulnerabilidad 3: Level 2 — Referencia Directa Insegura a Objetos / BOLA (owasp-3.py)

**2. Identificación y caracterización**

* **Descripción:** El endpoint PUT /profile actualizaba los datos de un usuario buscando el registro mediante el campo username enviado por el cliente en el cuerpo JSON, en lugar de usar la identidad verificada y firmada criptográficamente de la sesión activa.
* **Riesgo de seguridad asociado:** Alto. Brecha de confidencialidad e integridad (Modificación no autorizada de datos personales de terceros).
* **Categoría OWASP:** API1:2023 — Broken Object Level Authorization (BOLA/IDOR).
* **Impacto potencial:** Un atacante autenticado podía enviar el username de otro usuario (por ejemplo, chef) y sobrescribir su contraseña o correo electrónico, tomando el control completo de esa cuenta. Esta técnica puede combinarse con herramientas de enumeración como Burp Suite Intruder para identificar usuarios válidos del sistema.

**3. Análisis técnico y ético**

* **Origen de la vulnerabilidad:** Diseño e Implementación. Confianza excesiva en la entrada del cliente (Client-side trust). El servidor nunca verificaba si el usuario autenticado era el propietario legítimo del recurso que intentaba modificar.
* **Responsabilidad Ética:** Permitir a los usuarios dictar sobre qué objetos actúan sin validar la propiedad (ownership) transgrede normativas internacionales de protección de datos (ej. GDPR, Ley 1581 de Colombia) y expone legalmente a la empresa ante terceros afectados.

**4. Propuesta y aplicación de mitigación**

* **Refactorización:** Se eliminó la búsqueda en base de datos por username externo (get_user_by_username). En su lugar, el objeto a editar es el propio current_user inyectado directamente por el middleware de autenticación JWT.
* **Controles aplicados:** Autorización basada en propiedad del recurso (ownership validation) y validación estricta de parámetros permitidos.
Justificación: Al anclar la acción al contexto criptográfico del token de sesión (current_user), resulta matemáticamente imposible que un atacante altere el perfil de alguien más a menos que comprometa el token JWT de esa persona. El servidor nunca confía en un identificador proveniente del cliente.

**5. Validación de la solución**

* **Verificación:** Un intento de alterar un perfil enviando un username distinto al del token activo ahora solo modificará los datos del propio solicitante. La referencia directa insegura a objetos ha sido eliminada y el BOLA queda neutralizado.


### Vulnerabilidad 4: Level 3 — Escalada de Privilegios por Asignación Masiva / BOPLA (owasp-4.py)

**2. Identificación y caracterización**

* **Descripción:** El endpoint PATCH /profile aceptaba y procesaba sin filtrado cualquier campo del modelo de usuario incluido en el cuerpo de la solicitud. Esto permitía a un atacante añadir el campo role al JSON de la petición y asignarse directamente el rol de CHEF, saltándose completamente el modelo de control de acceso del sistema.
* **Riesgo de seguridad asociado:** Crítico. Toma de control total del sistema (Account Takeover y compromiso completo del modelo de permisos).
* **Categoría OWASP:** API3:2023 — Broken Object Property Level Authorization (BOPLA) / Mass Assignment.
* **Impacto potencial:** Un atacante puede elevar los privilegios de su cuenta de Customer a Chef (administrador raíz del sistema) con una sola petición HTTP, otorgándose acceso a todos los endpoints administrativos, incluyendo los que exponen funcionalidades de ejecución de comandos en el servidor.

**3. Análisis técnico y ético**

* **Origen de la vulnerabilidad:** Implementación. El desarrollador no utilizó un schema de validación (Pydantic schema) que listara explícitamente los campos modificables, permitiendo que el ORM mapeara automáticamente cualquier propiedad recibida al modelo de base de datos.
* **Responsabilidad Ética:** El ingeniero de software falló en implementar el principio de "denegación por defecto" (Default Deny) a nivel de propiedades del objeto. Permitir que cualquier campo del modelo de datos sea modificable desde el exterior es un fallo arquitectónico que invalida toda la jerarquía de roles del sistema.

**4. Propuesta y aplicación de mitigación**

* **Refactorización:** Se definió un schema Pydantic estricto (ProfileUpdate) que lista explícitamente únicamente los campos que un usuario puede modificar (email, full_name). El campo role no aparece en el schema y por tanto no puede ser asignado desde el exterior.
* **Controles aplicados:** Allowlist de propiedades modificables mediante schema de validación con extra = 'forbid'.
* **Justificación:** Al usar extra='forbid' en el modelo Pydantic, cualquier campo no declarado explícitamente en el schema (como role, is_active o balance) genera automáticamente un error HTTP 422 Unprocessable Entity antes de que la solicitud llegue a la capa de base de datos.

**5. Validación de la solución**

* **Verificación:** Un PATCH /profile enviando el campo "role": "CHEF" en el cuerpo retorna HTTP 422 Unprocessable Entity. La escalada de privilegios por asignación masiva es imposible. El modelo de roles del sistema queda íntegro.


### Vulnerabilidad 5: Level 4 — Falsificación de Solicitudes del Lado del Servidor / SSRF (owasp-5.py)

**2. Identificación y caracterización**

* **Descripción:** El endpoint de creación/modificación de platos del menú (PUT /menu) aceptaba un parámetro image_url que el servidor utilizaba para descargar la imagen del plato de forma remota. Al no validar ni restringir la URL proporcionada, un atacante con rol de Employee podía forzar al servidor a realizar peticiones HTTP arbitrarias hacia servicios internos que de otra forma serían inaccesibles desde el exterior de la red.
* **Riesgo de seguridad asociado:** Crítico. Acceso a recursos internos de red y compromiso de credenciales administrativas.
* **Categoría OWASP:** API7:2023 — Server Side Request Forgery (SSRF).
* **Impacto potencial:** El servidor actúa como proxy involuntario para el atacante. En este sistema, el endpoint interno http://localhost:8080/admin/reset-chef-password permite resetear la contraseña del Chef. Al enviarlo como image_url, el atacante fuerza al servidor a ejecutar esa petición en su propio contexto, obteniendo las credenciales del administrador. Este vector también puede usarse para escanear puertos internos o acceder a servicios de metadatos en la nube (AWS: 169.254.169.254).

**3. Análisis técnico y ético**

* **Origen de la vulnerabilidad:** Diseño. El servidor no distingue entre URLs externas legítimas y URLs internas maliciosas al momento de procesar el parámetro. Desde la perspectiva del servicio interno, la petición parece completamente legítima porque proviene del localhost del propio servidor.
* **Responsabilidad Ética:** El ingeniero de software que diseña funcionalidades de descarga remota de recursos tiene la obligación de implementar controles de validación de destino. No hacerlo viola el principio de aislamiento de red y puede resultar en el compromiso de toda la infraestructura interna de la organización.

**4. Propuesta y aplicación de mitigación**

* **Refactorización:** Se implementó una función de validación de URL que verifica el hostname de destino antes de ejecutar cualquier petición remota. Se bloquean explícitamente las direcciones de loopback (localhost, 127.0.0.1), rangos de IP privados y se aplica una allowlist de dominios externos permitidos.
* **Controles aplicados:** Allowlist estricta de dominios autorizados + bloqueo de direcciones IP privadas y de loopback.
* **Justificación:** Al validar el hostname antes de realizar la petición, el servidor rechaza cualquier URL que apunte a su propia red interna. Esto impide que el servidor sea utilizado como vector de acceso lateral hacia servicios no expuestos públicamente.

**5. Validación de la solución**

* **Verificación:** El envío de "image_url": "http://localhost:8080/admin/reset-chef-password" retorna HTTP 400 Bad Request con el mensaje "URL no permitida". El vector SSRF queda neutralizado y la contraseña del Chef permanece protegida.


### Vulnerabilidad 6: Level 5 — Inyección de Comandos del Sistema Operativo / RCE (owasp-6.py)

**2. Identificación y caracterización**

* **Descripción:** La función get_disk_usage tomaba el parámetro parameters directamente de la solicitud del usuario, lo concatenaba al string "df -h " y ejecutaba el resultado completo en una shell del sistema operativo mediante subprocess.run(shell=True). Esto permite a cualquier usuario autenticado como Chef inyectar comandos arbitrarios del sistema operativo en el servidor.
* **Riesgo de seguridad asociado:** Crítico. Permite Ejecución Remota de Código (RCE). Compromiso total de la Tríada CIA (Confidencialidad, Integridad y Disponibilidad).
* **Categoría OWASP:** API8:2023 — Security Misconfiguration / A03:2021 — Injection (OS Command Injection).
* **Impacto potencial:** El atacante obtiene una shell interactiva en el servidor con los mismos privilegios del proceso de la aplicación. Combinado con la configuración de sudo encontrada en el sistema (sudo /usr/bin/find sin contraseña), el atacante puede escalar a root y tomar control absoluto del servidor host, exfiltrar bases de datos completas, instalar ransomware o pivotar hacia la red interna de la organización.

**3. Análisis técnico y ético**

* **Origen de la vulnerabilidad:** Diseño e Implementación. El desarrollador utilizó shell=True por conveniencia y construyó el comando mediante concatenación de strings sin ningún tipo de sanitización del input. Esta combinación es reconocida como un antipatrón crítico de seguridad en toda la documentación oficial de Python.
* **Responsabilidad Ética:** Construir puentes directos e incontrolados entre la entrada externa del usuario y el shell del sistema operativo es una práctica inaceptable. El ingeniero pone en riesgo no solo la API, sino la infraestructura completa, los datos sensibles de todos los usuarios y la continuidad operativa de la organización. La existencia de este endpoint en producción constituiría una violación grave de los estándares de desarrollo seguro.

**4. Propuesta y aplicación de mitigación**

* **Refactorización:** Se eliminó por completo la dependencia del shell interpretado. El string de comando se transformó en una lista estricta de argumentos ["df", "-h", path] y se removió la bandera shell=True. Adicionalmente, se implementó una allowlist de rutas válidas que puede recibir el parámetro.
* **Controles aplicados:** Separación estricta entre "Comando" y "Argumentos" a nivel de la API del Sistema Operativo + allowlist de rutas permitidas + eliminación del intérprete de shell.
* **Justificación:** Al pasar una lista de argumentos directamente al kernel subyacente (sin pasar por bash/sh), cualquier carácter especial inyectado (como ;, |, &&, $()) pierde completamente su poder destructivo y es tratado puramente como texto literal inofensivo. El kernel no interpreta metacaracteres del shell cuando recibe los argumentos de forma separada.

**5. Validación de la solución**

* **Verificación:** Si un usuario envía un payload como ; cat /etc/passwd como parámetro, el binario df simplemente intentará (y fallará) buscar un dispositivo de disco llamado exactamente ; cat /etc/passwd, generando un error controlado del programa. Si la ruta no está en la allowlist, el sistema retorna HTTP 400 antes de ejecutar ningún proceso. La ejecución remota de código queda detenida exitosamente.