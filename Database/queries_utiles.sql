-- ================================================================
-- PATHWISE - Queries SQL Útiles
-- Base de Datos con Email como ID y Verificación de Estudiantes
-- ================================================================

-- ----------------------------------------------------------------
-- INSERCIÓN DE DATOS
-- ----------------------------------------------------------------

-- Insertar usuario con email institucional
INSERT INTO usuarios 
(email, nombre, escuela, grado_actual, area, community_tipo, requiere_verificacion_estudiante)
VALUES 
('maria.garcia@unam.mx', 'María García', 'Universidad Nacional Autónoma de México', 
 'Licenciatura', 'Ingeniería', 'Estudiantes STEM', 'SI');

-- Insertar usuario con email personal
INSERT INTO usuarios 
(email, nombre, escuela, grado_actual, area, community_tipo, requiere_verificacion_estudiante)
VALUES 
('juan.perez@gmail.com', 'Juan Pérez', 'Preparatoria Federal', 
 'Preparatoria', 'Humanidades', 'Estudiantes General', 'NO');

-- Insertar múltiples usuarios
INSERT INTO usuarios (email, nombre, escuela, grado_actual, area, requiere_verificacion_estudiante)
VALUES 
    ('ana.martinez@tec.mx', 'Ana Martínez', 'Tecnológico de Monterrey', 'Licenciatura', 'Negocios', 'SI'),
    ('carlos.lopez@ipn.mx', 'Carlos López', 'Instituto Politécnico Nacional', 'Ingeniería', 'Tecnología', 'SI'),
    ('laura.sanchez@hotmail.com', 'Laura Sánchez', 'CETIS 32', 'Preparatoria', 'Tecnología', 'NO');


-- ----------------------------------------------------------------
-- CONSULTAS BÁSICAS
-- ----------------------------------------------------------------

-- Ver todos los usuarios
SELECT * FROM usuarios;

-- Ver solo usuarios que requieren verificación
SELECT email, nombre, escuela 
FROM usuarios 
WHERE requiere_verificacion_estudiante = 'SI';

-- Ver usuarios que NO requieren verificación
SELECT email, nombre, escuela 
FROM usuarios 
WHERE requiere_verificacion_estudiante = 'NO';

-- Contar usuarios por tipo de verificación
SELECT 
    requiere_verificacion_estudiante,
    COUNT(*) as total
FROM usuarios
GROUP BY requiere_verificacion_estudiante;

-- Buscar usuario por email
SELECT * FROM usuarios WHERE email = 'maria.garcia@unam.mx';

-- Buscar usuarios por dominio de email
SELECT * FROM usuarios WHERE email LIKE '%@unam.mx';


-- ----------------------------------------------------------------
-- CONSULTAS AVANZADAS
-- ----------------------------------------------------------------

-- Usuarios por institución educativa
SELECT 
    escuela,
    COUNT(*) as total_estudiantes,
    SUM(CASE WHEN requiere_verificacion_estudiante = 'SI' THEN 1 ELSE 0 END) as con_verificacion,
    SUM(CASE WHEN requiere_verificacion_estudiante = 'NO' THEN 1 ELSE 0 END) as sin_verificacion
FROM usuarios
GROUP BY escuela
ORDER BY total_estudiantes DESC;

-- Usuarios por área de estudio
SELECT 
    area,
    COUNT(*) as total,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM usuarios), 2) as porcentaje
FROM usuarios
WHERE area IS NOT NULL
GROUP BY area
ORDER BY total DESC;

-- Usuarios por grado académico
SELECT 
    grado_actual,
    COUNT(*) as total
FROM usuarios
GROUP BY grado_actual
ORDER BY total DESC;

-- Top 10 dominios de email más usados
SELECT 
    SUBSTR(email, INSTR(email, '@') + 1) as dominio,
    COUNT(*) as total_usuarios
FROM usuarios
GROUP BY dominio
ORDER BY total_usuarios DESC
LIMIT 10;


-- ----------------------------------------------------------------
-- VERIFICACIÓN Y VALIDACIÓN
-- ----------------------------------------------------------------

-- Usuarios con emails institucionales (.edu o .edu.mx)
SELECT email, nombre, escuela
FROM usuarios
WHERE email LIKE '%.edu%'
   OR email LIKE '%.edu.mx';

-- Detectar posibles inconsistencias (email personal pero escuela institucional)
SELECT email, nombre, escuela
FROM usuarios
WHERE requiere_verificacion_estudiante = 'NO'
  AND (
    escuela LIKE '%universidad%' 
    OR escuela LIKE '%instituto%'
    OR escuela LIKE '%tecnológico%'
  );

-- Usuarios sin email válido (formato incorrecto)
SELECT email, nombre
FROM usuarios
WHERE email NOT LIKE '%@%' 
   OR email NOT LIKE '%.%';


-- ----------------------------------------------------------------
-- ROADMAP Y EXPERIENCIAS
-- ----------------------------------------------------------------

-- Insertar roadmap para un usuario
INSERT INTO roadmap_materias (email_usuario, tipo, materia, tema)
VALUES 
('maria.garcia@unam.mx', 'Matemáticas', 'Cálculo Diferencial', 'Límites y Continuidad');

-- Ver roadmap completo de un usuario
SELECT 
    r.tipo,
    r.materia,
    r.tema,
    u.nombre,
    u.escuela
FROM roadmap_materias r
JOIN usuarios u ON r.email_usuario = u.email
WHERE r.email_usuario = 'maria.garcia@unam.mx';

-- Insertar experiencia para un usuario
INSERT INTO cv_experiencias (email_usuario, tipo, tiene, cantidad, area)
VALUES 
('maria.garcia@unam.mx', 'Proyecto', 1, 3, 'Desarrollo Web');

-- Ver CV completo de un usuario
SELECT 
    e.tipo,
    e.tiene,
    e.cantidad,
    e.area,
    u.nombre
FROM cv_experiencias e
JOIN usuarios u ON e.email_usuario = u.email
WHERE e.email_usuario = 'maria.garcia@unam.mx';


-- ----------------------------------------------------------------
-- REPORTES Y ESTADÍSTICAS
-- ----------------------------------------------------------------

-- Dashboard general
SELECT 
    'Total Usuarios' as metrica, 
    COUNT(*) as valor 
FROM usuarios
UNION ALL
SELECT 
    'Requieren Verificación', 
    COUNT(*) 
FROM usuarios 
WHERE requiere_verificacion_estudiante = 'SI'
UNION ALL
SELECT 
    'Verificados (No Requieren)', 
    COUNT(*) 
FROM usuarios 
WHERE requiere_verificacion_estudiante = 'NO'
UNION ALL
SELECT 
    'Con Roadmap', 
    COUNT(DISTINCT email_usuario) 
FROM roadmap_materias
UNION ALL
SELECT 
    'Con Experiencias', 
    COUNT(DISTINCT email_usuario) 
FROM cv_experiencias;

-- Usuarios más activos (con más materias en roadmap)
SELECT 
    u.email,
    u.nombre,
    COUNT(r.id_roadmap) as total_materias
FROM usuarios u
LEFT JOIN roadmap_materias r ON u.email = r.email_usuario
GROUP BY u.email, u.nombre
HAVING COUNT(r.id_roadmap) > 0
ORDER BY total_materias DESC
LIMIT 10;

-- Materias más populares
SELECT 
    materia,
    COUNT(*) as estudiantes_inscritos
FROM roadmap_materias
GROUP BY materia
ORDER BY estudiantes_inscritos DESC
LIMIT 10;


-- ----------------------------------------------------------------
-- ACTUALIZACIÓN DE DATOS
-- ----------------------------------------------------------------

-- Cambiar el email de un usuario (clave primaria)
-- Nota: Esto actualizará automáticamente las referencias en otras tablas
UPDATE usuarios 
SET email = 'nuevo.email@unam.mx'
WHERE email = 'viejo.email@unam.mx';

-- Actualizar estatus de verificación
UPDATE usuarios 
SET requiere_verificacion_estudiante = 'SI'
WHERE email = 'usuario@ejemplo.mx';

-- Actualizar información de usuario
UPDATE usuarios 
SET nombre = 'María García López',
    grado_actual = 'Maestría',
    area = 'Inteligencia Artificial'
WHERE email = 'maria.garcia@unam.mx';


-- ----------------------------------------------------------------
-- ELIMINACIÓN DE DATOS (USAR CON PRECAUCIÓN)
-- ----------------------------------------------------------------

-- Eliminar usuario (eliminará también sus roadmaps y experiencias por cascade)
DELETE FROM usuarios WHERE email = 'usuario@eliminar.mx';

-- Eliminar roadmap específico
DELETE FROM roadmap_materias WHERE id_roadmap = 123;

-- Eliminar todas las experiencias de un usuario
DELETE FROM cv_experiencias WHERE email_usuario = 'usuario@ejemplo.mx';


-- ----------------------------------------------------------------
-- VISTAS ÚTILES
-- ----------------------------------------------------------------

-- Vista: Usuarios verificados con su información completa
CREATE VIEW IF NOT EXISTS usuarios_verificados AS
SELECT 
    email,
    nombre,
    escuela,
    grado_actual,
    area,
    community_tipo
FROM usuarios
WHERE requiere_verificacion_estudiante = 'SI';

-- Vista: Perfil completo de usuario
CREATE VIEW IF NOT EXISTS perfil_completo AS
SELECT 
    u.email,
    u.nombre,
    u.escuela,
    u.grado_actual,
    u.area,
    u.requiere_verificacion_estudiante,
    COUNT(DISTINCT r.id_roadmap) as total_materias,
    COUNT(DISTINCT e.id_experiencia) as total_experiencias
FROM usuarios u
LEFT JOIN roadmap_materias r ON u.email = r.email_usuario
LEFT JOIN cv_experiencias e ON u.email = e.email_usuario
GROUP BY u.email, u.nombre, u.escuela, u.grado_actual, u.area, u.requiere_verificacion_estudiante;

-- Usar las vistas
SELECT * FROM usuarios_verificados;
SELECT * FROM perfil_completo WHERE total_materias > 0;


-- ----------------------------------------------------------------
-- BÚSQUEDAS Y FILTROS
-- ----------------------------------------------------------------

-- Búsqueda por nombre (case insensitive)
SELECT * FROM usuarios 
WHERE LOWER(nombre) LIKE LOWER('%María%');

-- Búsqueda por escuela
SELECT * FROM usuarios 
WHERE LOWER(escuela) LIKE LOWER('%UNAM%');

-- Usuarios de una institución específica que requieren verificación
SELECT * FROM usuarios 
WHERE escuela LIKE '%Politécnico%' 
  AND requiere_verificacion_estudiante = 'SI';

-- Usuarios por community tipo
SELECT community_tipo, COUNT(*) as total
FROM usuarios
WHERE community_tipo IS NOT NULL
GROUP BY community_tipo;


-- ----------------------------------------------------------------
-- ÍNDICES PARA MEJOR RENDIMIENTO
-- ----------------------------------------------------------------

-- Índice en escuela para búsquedas rápidas
CREATE INDEX IF NOT EXISTS idx_usuarios_escuela ON usuarios(escuela);

-- Índice en verificación para filtros
CREATE INDEX IF NOT EXISTS idx_usuarios_verificacion ON usuarios(requiere_verificacion_estudiante);

-- Índice en área para análisis
CREATE INDEX IF NOT EXISTS idx_usuarios_area ON usuarios(area);

-- Índice en email_usuario para joins rápidos
CREATE INDEX IF NOT EXISTS idx_roadmap_email ON roadmap_materias(email_usuario);
CREATE INDEX IF NOT EXISTS idx_experiencias_email ON cv_experiencias(email_usuario);


-- ================================================================
-- FIN DEL SCRIPT
-- ================================================================
