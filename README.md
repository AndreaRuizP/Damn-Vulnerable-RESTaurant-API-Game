# Proyecto Final de Curso: Análisis y Mitigación de Vulnerabilidades

## 1. Selección del Sistema Vulnerable
*   **Nombre del Sistema:** Damn Vulnerable RESTaurant API Game
*   **Tipo de Aplicación:** API RESTful (Backend) construida con Python (FastAPI) y PostgreSQL.
*   **Descripción General y Propósito:** Es una plataforma de entrenamiento desarrollada de forma intencionalmente insegura. Simula el sistema de gestión de un restaurante (creación de platos, órdenes, perfiles de usuario y asignación de roles como Chef o Empleado). Su propósito principal es servir como un entorno controlado ("caja de arena") para que ingenieros de software e investigadores de ciberseguridad puedan detectar, explotar y, posteriormente, mitigar vulnerabilidades basadas en el OWASP API Security Top 10.
 
## Contexto del Problema
Las interfaces de programación de aplicaciones (APIs) se han convertido en el eje central de los sistemas de software modernos, permitiendo la comunicación entre componentes, la integración con terceros y la exposición de funcionalidades de negocio a través de la red. Sin embargo, esta centralidad las convierte también en uno de los vectores de ataque más explotados en la actualidad.

En el sector de restaurantes, la digitalización de operaciones críticas —como el registro de usuarios, la autenticación, la administración del menú y el control de roles internos— a través de APIs web expone a las organizaciones a riesgos significativos si dichas interfaces no son diseñadas, implementadas y configuradas siguiendo principios de seguridad sólidos.

El proyecto Damn Vulnerable RESTaurant API, construido con Python FastAPI y PostgreSQL, representa un entorno deliberadamente inseguro que reproduce vulnerabilidades reales identificadas en sistemas productivos del sector. Este sistema constituye el objeto de análisis del presente trabajo, cuyo propósito es identificar y relacionar sus fallas de seguridad con el estándar OWASP API Security Top 10 (2023), la referencia más actualizada y reconocida a nivel mundial para la evaluación de riesgos en APIs.

El OWASP API Security Top 10 (2023) identifica las diez categorías de riesgo más críticas en APIs, entre las que se destacan: la autorización rota a nivel de objeto (API1), la autenticación deficiente (API2), la autorización rota a nivel de propiedades de objeto (API3), el consumo irrestricto de recursos (API4), la autorización rota a nivel de función (API5), el acceso irrestricto a flujos de negocio sensibles (API6), la falsificación de solicitudes del lado del servidor (API7), la mala configuración de seguridad (API8), la gestión inadecuada del inventario de APIs (API9) y el consumo inseguro de APIs de terceros (API10).

La explotación de cualquiera de estas vulnerabilidades en el contexto de la plataforma analizada puede comprometer la confidencialidad de datos de usuarios y del negocio, la integridad de las operaciones (como la manipulación del menú o la escalada de privilegios), y la disponibilidad del servicio, con consecuencias directas sobre la confianza de los clientes y la responsabilidad legal de la organización.

El equipo de ingeniería de software tiene como misión realizar un análisis técnico sistemático de las vulnerabilidades presentes en el sistema, clasificarlas según el estándar mencionado y proponer soluciones concretas que reduzcan el nivel de riesgo a uno aceptable para la operación segura del negocio.
---

## Análisis de Vulnerabilidades Encontradas

A continuación, se detalla el análisis y corrección de cinco (5) vulnerabilidades críticas halladas en el sistema, cumpliendo con las rúbricas de evaluación.

---

### Vulnerabilidad 1: Exposición de Información Sensible (owasp-1.py)

**2. Identificación y caracterización**
*   **Descripción:** El endpoint de estado (`/healthcheck`) inyectaba manualmente una cabecera HTTP (`X-Powered-By`) revelando que el servidor corría con "Python 3.10 y FastAPI ^0.103.0".
*   **Riesgo de seguridad asociado:** Medio. Facilita la fase de reconocimiento (enumeración pasiva) para un atacante.
*   **Categoría OWASP:** Security Misconfiguration (OWASP Top 10 Web) / Information Exposure.
*   **Impacto potencial:** Si se descubre un fallo de día cero (0-day) en esa versión específica de FastAPI, los atacantes pueden buscar en Internet servidores que expongan esa cabecera y atacarlos con exploits automatizados de forma masiva.

**3. Análisis técnico y ético**
*   **Origen de la vulnerabilidad:** Implementación. El desarrollador añadió metadatos técnicos en el código productivo.
*   **Responsabilidad Ética:** Un ingeniero de software debe guiarse por el principio de mínima divulgación. Exponer información interna por vanidad tecnológica o descuidos de depuración compromete la infraestructura de la empresa.

**4. Propuesta y aplicación de mitigación**
*   **Refactorización:** Se eliminó la inyección de las cabeceras `response.headers["X-Powered-By"]`.
*   **Controles aplicados:** Sanitización de respuestas HTTP.
*   **Justificación:** Limitar los metadatos incrementa el costo y el esfuerzo de un atacante para descubrir qué vulnerabilidades afectan a la infraestructura (Security through obscurity, que aunque no es defensa absoluta, es una buena práctica de hardening).

**5. Validación de la solución**
*   **Verificación:** El endpoint ahora retorna exclusivamente el payload `{"ok": True}`. Una inspección con herramientas como `curl -I` evidencia la ausencia de la cabecera `X-Powered-By`, validando la corrección.

---

### Vulnerabilidad 2: Falta de Autorización a Nivel de Función (owasp-2.py)

**2. Identificación y caracterización**
*   **Descripción:** El endpoint `PUT /menu/{item_id}` requería autenticación (estar logueado), pero no validaba el rol del usuario para actualizar platos.
*   **Riesgo de seguridad asociado:** Alto. Riesgo crítico a la integridad del negocio.
*   **Categoría OWASP:** API5:2023 - Broken Function Level Authorization (BFLA).
*   **Impacto potencial:** Cualquier cliente registrado podría alterar el nombre, descripción y bajar el precio de cualquier plato a cero, generando fraude comercial severo.

**3. Análisis técnico y ético**
*   **Origen de la vulnerabilidad:** Diseño de seguridad incompleto (Autenticación sin Autorización).
*   **Responsabilidad Ética:** El ingeniero es responsable de diferenciar entre "saber quién eres" (autenticación) y "saber qué puedes hacer" (autorización). Omitir esta validación es negligencia técnica.

**4. Propuesta y aplicación de mitigación**
*   **Refactorización:** Se inyectó un middleware de dependencias `auth=Depends(RolesBasedAuthChecker([UserRole.EMPLOYEE, UserRole.CHEF]))`.
*   **Controles aplicados:** Control de Acceso Basado en Roles (RBAC).
*   **Justificación:** Centraliza la lógica de permisos. FastApi interceptará la solicitud y si el JWT del usuario no contiene el rol de Empleado o Chef, rechazará la petición automáticamente.

**5. Validación de la solución**
*   **Verificación:** Si un usuario con rol estándar (`USER`) realiza un `PUT /menu/1`, el sistema retorna un error HTTP 403 Forbidden. La vulnerabilidad queda reducida a cero.

---

### Vulnerabilidad 3: Insecure Direct Object Reference / BOLA (owasp-3.py)

**2. Identificación y caracterización**
*   **Descripción:** El endpoint `/profile` actualizaba los datos de un usuario buscando el registro mediante el campo `username` enviado por el cliente en el JSON, en lugar de usar la identidad verificada de la sesión.
*   **Riesgo de seguridad asociado:** Alto. Brecha de confidencialidad e integridad (Modificación no autorizada de datos personales).
*   **Categoría OWASP:** API1:2023 - Broken Object Level Authorization (BOLA/IDOR).
*   **Impacto potencial:** Un atacante autenticado podía enviar el nombre de usuario de otro cliente y sobrescribir su perfil, robar su cuenta o manipular sus datos.

**3. Análisis técnico y ético**
*   **Origen de la vulnerabilidad:** Diseño e Implementación. Confianza excesiva en la entrada del cliente (Client-side trust).
*   **Responsabilidad Ética:** Permitir a los usuarios dictar sobre qué objetos actúan sin validar la propiedad (ownership) transgrede normativas de protección de datos (ej. GDPR) y expone legalmente a la empresa.

**4. Propuesta y aplicación de mitigación**
*   **Refactorización:** Se eliminó la búsqueda en base de datos (`get_user_by_username`). En su lugar, el objeto a editar es el propio `current_user` inyectado por el middleware de seguridad.
*   **Controles aplicados:** Autorización basada en propiedad del recurso y validación estricta de parámetros permitidos.
*   **Justificación:** Al anclar la acción al contexto criptográfico del token de sesión (`current_user`), resulta matemáticamente imposible que un atacante altere el perfil de alguien más a menos que comprometa su token JWT.

**5. Validación de la solución**
*   **Verificación:** Un intento de alterar un perfil enviando un username distinto ahora solo modificará los datos del propio atacante. El BOLA ha sido eliminado.

---

### Vulnerabilidad 4: Escalada de Privilegios / BFLA (owasp-4.py)

**2. Identificación y caracterización**
*   **Descripción:** El endpoint `/users/update_role` no tenía verificador de roles en la ruta. Solo bloqueaba la creación manual de un usuario `CHEF`, pero permitía a cualquiera asignar roles de `EMPLOYEE`.
*   **Riesgo de seguridad asociado:** Crítico. Toma de control del sistema (Account Takeover y compromiso total del modelo de permisos).
*   **Categoría OWASP:** API5:2023 - Broken Function Level Authorization (BFLA).
*   **Impacto potencial:** Un atacante puede elevar los permisos de su cuenta de usuario normal a cuenta administrativa, saltándose todas las barreras posteriores de la plataforma.

**3. Análisis técnico y ético**
*   **Origen de la vulnerabilidad:** Implementación (Lógica de validación incompleta).
*   **Responsabilidad Ética:** El ingeniero de software falló en implementar un enfoque de "denegación por defecto" (Default Deny). La ausencia de controles estrictos en endpoints de administración es un fallo arquitectónico severo.

**4. Propuesta y aplicación de mitigación**
*   **Refactorización:** Se protegió la ruta exigiendo explícitamente el rol máximo: `auth=Depends(RolesBasedAuthChecker([models.UserRole.CHEF]))`.
*   **Controles aplicados:** RBAC estricto en el endpoint.
*   **Justificación:** Se traslada la seguridad al nivel de enrutamiento (Gateway). Solo el administrador central (`CHEF`) puede invocar la lógica que modifica roles, garantizando el aislamiento de funciones privilegiadas.

**5. Validación de la solución**
*   **Verificación:** Las cuentas comunes ahora reciben un HTTP 403. Únicamente la cuenta raíz (`CHEF`) puede ejecutar esta transición de estados.

---

### Vulnerabilidad 5: Inyección de Comandos del Sistema Operativo (owasp-5.py)

**2. Identificación y caracterización**
*   **Descripción:** La función `get_disk_usage` tomaba parámetros del usuario, los unía a un string (`"df -h " + parameters`) y ejecutaba todo directamente en una shell del servidor (`subprocess.run(shell=True)`).
*   **Riesgo de seguridad asociado:** Crítico. Permite la Ejecución Remota de Código (RCE). Compromiso en la Tríada CIA completa.
*   **Categoría OWASP:** A03:2021 - Injection (OS Command Injection).
*   **Impacto potencial:** El atacante podría inyectar `; rm -rf /` o instalar ransomware, tomando control absoluto del servidor host y pivotando hacia la red interna de la empresa.

**3. Análisis técnico y ético**
*   **Origen de la vulnerabilidad:** Diseño e Implementación. El desarrollador utilizó librerías inseguras por conveniencia (`shell=True`) y falló en sanitizar el input.
*   **Responsabilidad Ética:** Construir puentes directos e incontrolados entre la entrada externa y el shell del SO es una práctica inaceptable. El ingeniero pone en riesgo no solo la API, sino la infraestructura completa y los datos sensibles de la organización.

**4. Propuesta y aplicación de mitigación**
*   **Refactorización:** Se eliminó la dependencia del shell interpretado. El string se transformó en una lista estricta `["df", "-h", parameters.split()]` y se removió la bandera `shell=True`.
*   **Controles aplicados:** Separación estricta entre "Comando" y "Argumentos" a nivel de la API del Sistema Operativo, evitando evaluación de metacaracteres.
*   **Justificación:** Al pasar una lista directamente al kernel subyacente (sin pasar por bash/sh), cualquier carácter especial inyectado (como `;`, `|`, `&&`) pierde su poder destructivo y es tratado puramente como un texto literal inofensivo.

**5. Validación de la solución**
*   **Verificación:** Si un usuario envía un payload destructivo como `; cat /etc/passwd`, el binario `df` simplemente intentará (y fallará) buscar un dispositivo de disco llamado `; cat /etc/passwd`, generando un error controlado del programa y deteniendo exitosamente la ejecución arbitraria.
