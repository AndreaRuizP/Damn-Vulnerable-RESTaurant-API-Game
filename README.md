# Reporte de Vulnerabilidades OWASP

Este documento detalla las vulnerabilidades encontradas y corregidas en el proyecto, clasificadas según el OWASP Top 10. Se explica la naturaleza de cada error, su peligro y la solución técnica implementada.

---

## 1. Exposición de Información Sensible (owasp-1.py)

**¿Cuál era el error original?**
El endpoint `/healthcheck` agregaba el encabezado HTTP `X-Powered-By: Python 3.10, FastAPI ^0.103.0` a la respuesta.

**¿De qué trata la vulnerabilidad?**
Consiste en revelar innecesariamente información sobre el stack tecnológico, versiones o infraestructura que soporta la aplicación.

**Clasificación OWASP**
* Security Misconfiguration / Information Exposure

**¿Por qué es peligroso?**
Facilita la fase de reconocimiento de un atacante. Si mañana se descubre una vulnerabilidad crítica en `FastAPI 0.103.0` o `Python 3.10`, el atacante sabrá inmediatamente que tu sistema es un blanco fácil y qué exploit exacto utilizar, sin tener que adivinar.

**¿Cómo se mitiga?**
Se elimina la asignación de encabezados informativos y la aplicación devuelve únicamente lo estrictamente necesario (ej. `{"ok": True}`).

---

## 2. Falta de Autorización a Nivel de Función (owasp-2.py)

**¿Cuál era el error original?**
El endpoint `PUT /menu/{item_id}` exigía que el usuario estuviera autenticado (`get_current_user`), pero **no verificaba el rol** del usuario.

**¿De qué trata la vulnerabilidad?**
Cualquier usuario con una cuenta válida (incluso un cliente normal) podía acceder a funciones administrativas, en este caso, alterar los elementos del menú.

**Clasificación OWASP**
* API5:2023 - Broken Function Level Authorization (BFLA)

**¿Por qué es peligroso?**
Permite a usuarios sin privilegios ejecutar funciones críticas de la lógica de negocio, lo que puede causar fraude económico (ej. cambiar el precio de un plato costoso a $0) o sabotaje.

**¿Cómo se mitiga?**
Se inyectó un middleware verificador de roles: `auth=Depends(RolesBasedAuthChecker([UserRole.EMPLOYEE, UserRole.CHEF]))`, el cual asegura que la función sea inaccesible para roles no autorizados.

---

## 3. Autorización Rota a Nivel de Objeto / BOLA (owasp-3.py)

**¿Cuál era el error original?**
El endpoint de actualizar perfil buscaba en la base de datos al usuario a modificar basándose en el parámetro proporcionado en la solicitud: `db_user = get_user_by_username(db, user.username)`.

**¿De qué trata la vulnerabilidad?**
También conocida como *Insecure Direct Object Reference* (IDOR). Un usuario autenticado podía enviar en su JSON el `username` de otra persona (ej. el del administrador) y modificar su perfil, ya que el sistema confiaba en la solicitud del cliente en lugar de usar el contexto seguro de la sesión.

**Clasificación OWASP**
* API1:2023 - Broken Object Level Authorization (BOLA)

**¿Por qué es peligroso?**
Permite la toma de control de cuentas ajenas, robo de identidad o la modificación malintencionada de datos privados de otros clientes sin su consentimiento.

**¿Cómo se mitiga?**
En lugar de buscar el registro en base al texto que envía el atacante, se impone el contexto criptográfico de autenticación vinculando la acción directamente a quien inició sesión: `db_user = current_user`.

---

## 4. Escalada de Privilegios (owasp-4.py)

**¿Cuál era el error original?**
El endpoint `update_user_role` no validaba qué tipo de usuario ejecutaba la solicitud. Simplemente bloqueaba el intento de asignar el rol de CHEF, pero permitía a cualquiera asignar el rol EMPLOYEE.

**¿De qué trata la vulnerabilidad?**
Un usuario normal podía asignarse a sí mismo (o a otros) roles administrativos superiores (escalada de privilegios vertical) al descubrir el endpoint oculto.

**Clasificación OWASP**
* API5:2023 - Broken Function Level Authorization (BFLA)

**¿Por qué es peligroso?**
Un atacante puede convertir una cuenta común en una cuenta de administración (empleado), comprometiendo la confidencialidad e integridad de todo el sistema y saltándose todas las barreras posteriores.

**¿Cómo se mitiga?**
Se blindó el endpoint completo exigiendo el rol máximo `auth=Depends(RolesBasedAuthChecker([models.UserRole.CHEF]))`, asegurando que solo el administrador principal pueda otorgar roles a terceros.

---

## 5. Inyección de Comandos del SO (owasp-5.py)

**¿Cuál era el error original?**
El código tomaba un input de texto del usuario (`parameters`) y lo concatenaba crudamente en un comando de shell: `command = "df -h " + parameters`, ejecutándolo luego a través de `subprocess.run(..., shell=True)`.

**¿De qué trata la vulnerabilidad?**
Al usar `shell=True`, el intérprete de comandos evalúa caracteres especiales (como `;`, `|`, `&&`). Un atacante podía enviar algo como `; rm -rf /` o `&& cat /etc/passwd`, alterando la naturaleza de la ejecución y forzando al sistema operativo a ejecutar código arbitrario.

**Clasificación OWASP**
* A03:2021 - Injection (OS Command Injection)

**¿Por qué es peligroso?**
Es una de las vulnerabilidades más letales (Remote Code Execution - RCE). El atacante toma el control absoluto del servidor subyacente. Puede exfiltrar bases de datos, instalar malware, borrar el sistema o usarlo para atacar la red interna corporativa.

**¿Cómo se mitiga?**
Se removió `shell=True` y se reestructuró el comando para ser una lista de strings de Python pura: `["df", "-h", parámetro_1, parámetro_2]`. De esta forma, el sistema operativo le quita la magia a los caracteres especiales y los interpreta puramente como texto inofensivo.
