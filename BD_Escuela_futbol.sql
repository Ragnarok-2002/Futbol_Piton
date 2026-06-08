-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 08-06-2026 a las 04:42:59
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `bd_escuela_futbol`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `acudiente`
--

CREATE TABLE `acudiente` (
  `id_acudiente` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `id_rol` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `apellido` varchar(100) NOT NULL,
  `documento` varchar(20) NOT NULL,
  `telefono` varchar(20) NOT NULL,
  `email` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `acudiente`
--

INSERT INTO `acudiente` (`id_acudiente`, `id_usuario`, `id_rol`, `nombre`, `apellido`, `documento`, `telefono`, `email`) VALUES
(1, 34, 5, 'Ricardo', 'Gómez', '10234561', '3101234001', 'padre.gomez@gmail.com'),
(2, 35, 5, 'Claudia', 'Ramírez', '42345672', '3101234002', 'madre.ramirez@gmail.com'),
(3, 36, 5, 'Hernando', 'Castro', '10234573', '3101234003', 'padre.castro@gmail.com'),
(4, 37, 5, 'Patricia', 'Ospina', '42345684', '3101234004', 'madre.ospina@gmail.com'),
(5, 38, 5, 'Roberto', 'Silva', '10234595', '3101234005', 'tutor.silva@gmail.com'),
(6, 39, 5, 'Gustavo', 'Lozano', '10234606', '3101234006', 'padre.lozano@gmail.com'),
(7, 40, 5, 'Marcela', 'Gutiérrez', '42345717', '3101234007', 'madre.gutierrez@gmail.com'),
(8, 41, 5, 'Fabio', 'Herrera', '10234628', '3101234008', 'padre.herrera@gmail.com'),
(9, 42, 5, 'Adriana', 'Mora', '42345739', '3101234009', 'madre.mora@gmail.com'),
(10, 43, 5, 'Diego', 'Ruiz', '10234640', '3101234010', 'tutor.ruiz@gmail.com'),
(11, 44, 5, 'Mauricio', 'Jiménez', '10234651', '3101234011', 'padre.jimenez@gmail.com'),
(12, 45, 5, 'Esperanza', 'Reyes', '42345762', '3101234012', 'madre.reyes@gmail.com'),
(13, 46, 5, 'Bernardo', 'Peña', '10234673', '3101234013', 'padre.pena@gmail.com'),
(14, 47, 5, 'Liliana', 'Cardona', '42345784', '3101234014', 'madre.cardona@gmail.com'),
(15, 48, 5, 'Henry', 'Flórez', '10234695', '3101234015', 'tutor.florez@gmail.com'),
(16, 49, 5, 'Jairo', 'Molina', '10234706', '3101234016', 'padre.molina@gmail.com'),
(17, 50, 5, 'Carmen', 'Arango', '42345817', '3101234017', 'madre.arango@gmail.com'),
(18, 51, 5, 'Nelson', 'Soto', '10234728', '3101234018', 'padre.soto@gmail.com'),
(19, 52, 5, 'Yolanda', 'Duque', '42345839', '3101234019', 'madre.duque@gmail.com'),
(20, 53, 5, 'Rodrigo', 'León', '10234740', '3101234020', 'tutor.leon@gmail.com'),
(21, 54, 5, 'Alberto', 'Salazar', '10234751', '3101234021', 'padre.salazar@gmail.com'),
(22, 55, 5, 'Gloria', 'Cerón', '42345862', '3101234022', 'madre.ceron@gmail.com'),
(23, 56, 5, 'Ernesto', 'Acosta', '10234773', '3101234023', 'padre.acosta@gmail.com'),
(24, 57, 5, 'Beatriz', 'Mendoza', '42345884', '3101234024', 'madre.mendoza@gmail.com'),
(25, 58, 5, 'Raúl', 'Zapata', '10234795', '3101234025', 'tutor.zapata@gmail.com');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `asistencia`
--

CREATE TABLE `asistencia` (
  `id_asistencia` int(11) NOT NULL,
  `id_entrenamiento` int(11) NOT NULL,
  `id_jugador` int(11) NOT NULL,
  `id_equipo` int(11) NOT NULL,
  `asistio` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `asistencia`
--

INSERT INTO `asistencia` (`id_asistencia`, `id_entrenamiento`, `id_jugador`, `id_equipo`, `asistio`) VALUES
(1, 1, 1, 1, 1),
(2, 2, 6, 2, 1),
(3, 3, 11, 3, 1),
(4, 4, 16, 4, 1),
(5, 5, 21, 5, 1),
(6, 6, 2, 1, 1),
(7, 7, 7, 2, 1),
(8, 8, 12, 3, 1),
(9, 9, 17, 4, 1),
(10, 10, 22, 5, 1),
(11, 11, 3, 1, 1),
(12, 11, 4, 1, 1),
(13, 12, 8, 2, 1),
(14, 12, 9, 2, 1),
(15, 13, 13, 3, 1),
(16, 13, 14, 3, 0),
(17, 14, 18, 4, 1),
(18, 14, 19, 4, 1),
(19, 15, 23, 5, 1),
(20, 15, 24, 5, 1),
(21, 16, 5, 1, 1),
(22, 17, 10, 2, 1),
(23, 18, 1, 1, 1),
(24, 18, 2, 1, 1),
(25, 18, 3, 1, 1),
(26, 18, 4, 1, 1),
(27, 18, 5, 1, 1),
(28, 19, 11, 3, 1),
(29, 19, 12, 3, 1),
(30, 19, 13, 3, 0),
(31, 19, 14, 3, 1),
(32, 19, 15, 3, 1),
(33, 20, 21, 5, 1),
(34, 20, 22, 5, 1),
(35, 20, 23, 5, 1),
(36, 20, 24, 5, 1),
(37, 20, 25, 5, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `detalle_pago`
--

CREATE TABLE `detalle_pago` (
  `id_detalle` int(11) NOT NULL,
  `id_pago` int(11) NOT NULL,
  `mes_correspondiente` varchar(50) NOT NULL,
  `subtotal` decimal(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `detalle_pago`
--

INSERT INTO `detalle_pago` (`id_detalle`, `id_pago`, `mes_correspondiente`, `subtotal`) VALUES
(1, 1, 'Enero 2025', 75000.00),
(2, 2, 'Febrero 2025', 75000.00),
(3, 3, 'Marzo 2025', 75000.00),
(4, 4, 'Enero 2025', 75000.00),
(5, 5, 'Febrero 2025', 75000.00),
(6, 6, 'Marzo 2025', 75000.00),
(7, 7, 'Enero 2025', 75000.00),
(8, 8, 'Febrero 2025', 75000.00),
(9, 9, 'Marzo 2025', 75000.00),
(10, 10, 'Enero 2025', 75000.00),
(11, 11, 'Febrero 2025', 75000.00),
(12, 12, 'Marzo 2025', 75000.00),
(13, 13, 'Enero 2025', 75000.00),
(14, 14, 'Febrero 2025', 75000.00),
(15, 15, 'Marzo 2025', 75000.00),
(16, 16, 'Enero 2025', 75000.00),
(17, 17, 'Febrero 2025', 75000.00),
(18, 18, 'Marzo 2025', 75000.00),
(19, 19, 'Enero 2025', 75000.00),
(20, 20, 'Febrero 2025', 75000.00),
(21, 21, 'Marzo 2025', 75000.00),
(22, 22, 'Enero 2025', 75000.00),
(23, 23, 'Febrero 2025', 75000.00),
(24, 24, 'Marzo 2025', 75000.00),
(25, 25, 'Enero 2025', 75000.00),
(26, 26, 'Febrero 2025', 75000.00),
(27, 27, 'Marzo 2025', 75000.00),
(28, 28, 'Enero 2025', 75000.00),
(29, 29, 'Febrero 2025', 75000.00),
(30, 30, 'Marzo 2025', 75000.00),
(31, 31, 'Enero 2025', 75000.00),
(32, 32, 'Febrero 2025', 75000.00),
(33, 33, 'Marzo 2025', 75000.00),
(34, 34, 'Enero 2025', 75000.00),
(35, 35, 'Febrero 2025', 75000.00),
(36, 36, 'Marzo 2025', 75000.00),
(37, 37, 'Enero 2025', 75000.00),
(38, 38, 'Febrero 2025', 75000.00),
(39, 39, 'Marzo 2025', 75000.00),
(40, 40, 'Enero 2025', 75000.00),
(41, 41, 'Febrero 2025', 75000.00),
(42, 42, 'Marzo 2025', 75000.00),
(43, 43, 'Enero 2025', 75000.00),
(44, 44, 'Febrero 2025', 75000.00),
(45, 45, 'Marzo 2025', 75000.00),
(46, 46, 'Enero 2025', 75000.00),
(47, 47, 'Febrero 2025', 75000.00),
(48, 48, 'Marzo 2025', 75000.00),
(49, 49, 'Enero 2025', 75000.00),
(50, 50, 'Febrero 2025', 75000.00),
(51, 51, 'Marzo 2025', 75000.00),
(52, 52, 'Enero 2025', 75000.00),
(53, 53, 'Febrero 2025', 75000.00),
(54, 54, 'Marzo 2025', 75000.00),
(55, 55, 'Enero 2025', 75000.00),
(56, 56, 'Febrero 2025', 75000.00),
(57, 57, 'Marzo 2025', 75000.00),
(58, 58, 'Enero 2025', 75000.00),
(59, 59, 'Febrero 2025', 75000.00),
(60, 60, 'Marzo 2025', 75000.00),
(61, 61, 'Enero 2025', 75000.00),
(62, 62, 'Febrero 2025', 75000.00),
(63, 63, 'Marzo 2025', 75000.00),
(64, 64, 'Enero 2025', 75000.00),
(65, 65, 'Febrero 2025', 75000.00),
(66, 66, 'Marzo 2025', 75000.00),
(67, 67, 'Enero 2025', 75000.00),
(68, 68, 'Febrero 2025', 75000.00),
(69, 69, 'Marzo 2025', 75000.00),
(70, 70, 'Enero 2025', 75000.00),
(71, 71, 'Febrero 2025', 75000.00),
(72, 72, 'Marzo 2025', 75000.00),
(73, 73, 'Enero 2025', 75000.00),
(74, 74, 'Febrero 2025', 75000.00),
(75, 75, 'Marzo 2025', 75000.00);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `entrenador`
--

CREATE TABLE `entrenador` (
  `id_entrenador` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `id_rol` int(11) NOT NULL,
  `nombres` varchar(100) NOT NULL,
  `apellidos` varchar(100) NOT NULL,
  `telefono` varchar(20) NOT NULL,
  `email` varchar(100) NOT NULL,
  `especialidad` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `entrenador`
--

INSERT INTO `entrenador` (`id_entrenador`, `id_usuario`, `id_rol`, `nombres`, `apellidos`, `telefono`, `email`, `especialidad`) VALUES
(1, 4, 3, 'Carlos', 'Ríos Mendoza', '3151230001', 'carlos.rios@escuelaaaa.com', 'Delanteros'),
(2, 5, 3, 'Jorge', 'Méndez Castaño', '3151230002', 'jorge.mendez@escuelaaaa.com', 'Mediocampistas'),
(3, 6, 3, 'Andrés', 'Vargas Ortega', '3151230003', 'andres.vargas@escuelaaaa.com', 'Defensas'),
(4, 7, 3, 'Luis', 'Pérez Acevedo', '3151230004', 'luis.perez@escuelaaaa.com', 'Porteros'),
(5, 8, 3, 'Miguel', 'Torres Suárez', '3151230005', 'miguel.torres@escuelaaaa.com', 'General');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `entrenamiento`
--

CREATE TABLE `entrenamiento` (
  `id_entrenamiento` int(11) NOT NULL,
  `id_entrenador` int(11) NOT NULL,
  `id_equipo` int(11) NOT NULL,
  `fecha` date NOT NULL,
  `ubicacion` varchar(100) NOT NULL,
  `tipo_entrenamiento` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `entrenamiento`
--

INSERT INTO `entrenamiento` (`id_entrenamiento`, `id_entrenador`, `id_equipo`, `fecha`, `ubicacion`, `tipo_entrenamiento`) VALUES
(1, 1, 1, '2025-01-06', 'Cancha Principal', 'Delanteros'),
(2, 1, 2, '2025-01-07', 'Cancha Auxiliar', 'Delanteros'),
(3, 1, 3, '2025-01-08', 'Cancha Principal', 'Delanteros'),
(4, 1, 4, '2025-01-09', 'Cancha Auxiliar', 'Delanteros'),
(5, 1, 5, '2025-01-10', 'Cancha Principal', 'Delanteros'),
(6, 2, 1, '2025-01-13', 'Cancha Auxiliar', 'Mediocampistas'),
(7, 2, 2, '2025-01-14', 'Cancha Principal', 'Mediocampistas'),
(8, 2, 3, '2025-01-15', 'Cancha Auxiliar', 'Mediocampistas'),
(9, 2, 4, '2025-01-16', 'Cancha Principal', 'Mediocampistas'),
(10, 2, 5, '2025-01-17', 'Cancha Auxiliar', 'Mediocampistas'),
(11, 3, 1, '2025-01-20', 'Cancha Principal', 'Defensas'),
(12, 3, 2, '2025-01-21', 'Cancha Auxiliar', 'Defensas'),
(13, 3, 3, '2025-01-22', 'Cancha Principal', 'Defensas'),
(14, 3, 4, '2025-01-23', 'Cancha Auxiliar', 'Defensas'),
(15, 3, 5, '2025-01-24', 'Cancha Principal', 'Defensas'),
(16, 4, 1, '2025-01-27', 'Cancha Auxiliar', 'Porteros'),
(17, 4, 2, '2025-01-28', 'Cancha Principal', 'Porteros'),
(18, 5, 1, '2025-02-03', 'Cancha Principal', 'General'),
(19, 5, 3, '2025-02-04', 'Cancha Auxiliar', 'General'),
(20, 5, 5, '2025-02-05', 'Cancha Principal', 'General');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `equipo`
--

CREATE TABLE `equipo` (
  `id_equipo` int(11) NOT NULL,
  `id_division` int(11) NOT NULL,
  `nombre_equipo` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `equipo`
--

INSERT INTO `equipo` (`id_equipo`, `id_division`, `nombre_equipo`) VALUES
(1, 1, 'AAA Sub-20'),
(2, 2, 'AAA Sub-18'),
(3, 3, 'AAA Sub-16'),
(4, 4, 'AAA Sub-14'),
(5, 5, 'AAA Sub-10');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `estado_jugador`
--

CREATE TABLE `estado_jugador` (
  `id_estado` int(11) NOT NULL,
  `disponibilidad` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `estado_jugador`
--

INSERT INTO `estado_jugador` (`id_estado`, `disponibilidad`) VALUES
(1, 'Disponible'),
(2, 'Lesionado'),
(3, 'Suspendido'),
(4, 'Inactivo');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `ficha_jugador`
--

CREATE TABLE `ficha_jugador` (
  `id_jugador` int(11) NOT NULL,
  `id_equipo` int(11) NOT NULL,
  `id_estado` int(11) NOT NULL,
  `posicion` varchar(50) NOT NULL,
  `estatura` decimal(4,2) NOT NULL,
  `peso` decimal(5,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `ficha_jugador`
--

INSERT INTO `ficha_jugador` (`id_jugador`, `id_equipo`, `id_estado`, `posicion`, `estatura`, `peso`) VALUES
(1, 1, 1, 'Delantero', 1.78, 72.00),
(2, 1, 1, 'Mediocampista', 1.74, 68.00),
(3, 1, 1, 'Defensa', 1.76, 70.00),
(4, 1, 1, 'Defensa', 1.75, 71.00),
(5, 1, 1, 'Portero', 1.82, 78.00),
(6, 2, 1, 'Delantero', 1.70, 65.00),
(7, 2, 1, 'Mediocampista', 1.68, 62.00),
(8, 2, 1, 'Defensa', 1.72, 67.00),
(9, 2, 1, 'Defensa', 1.71, 66.00),
(10, 2, 1, 'Portero', 1.76, 73.00),
(11, 3, 1, 'Delantero', 1.65, 58.00),
(12, 3, 1, 'Mediocampista', 1.63, 55.00),
(13, 3, 1, 'Defensa', 1.67, 60.00),
(14, 3, 1, 'Defensa', 1.66, 59.00),
(15, 3, 1, 'Portero', 1.70, 65.00),
(16, 4, 1, 'Delantero', 1.58, 50.00),
(17, 4, 1, 'Mediocampista', 1.56, 47.00),
(18, 4, 1, 'Defensa', 1.60, 52.00),
(19, 4, 1, 'Defensa', 1.59, 51.00),
(20, 4, 1, 'Portero', 1.63, 55.00),
(21, 5, 1, 'Delantero', 1.40, 35.00),
(22, 5, 1, 'Mediocampista', 1.38, 33.00),
(23, 5, 1, 'Defensa', 1.42, 36.00),
(24, 5, 1, 'Defensa', 1.41, 35.50),
(25, 5, 1, 'Portero', 1.45, 38.00);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `jugador`
--

CREATE TABLE `jugador` (
  `id_jugador` int(11) NOT NULL,
  `id_acudiente` int(11) DEFAULT NULL,
  `id_usuario` int(11) NOT NULL,
  `id_rol` int(11) NOT NULL,
  `nombres` varchar(100) NOT NULL,
  `apellidos` varchar(100) NOT NULL,
  `fecha_nacimiento` date NOT NULL,
  `telefono` varchar(20) NOT NULL,
  `email` varchar(100) NOT NULL,
  `documento` varchar(20) NOT NULL,
  `fecha_registro` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `jugador`
--

INSERT INTO `jugador` (`id_jugador`, `id_acudiente`, `id_usuario`, `id_rol`, `nombres`, `apellidos`, `fecha_nacimiento`, `telefono`, `email`, `documento`, `fecha_registro`) VALUES
(1, 1, 9, 4, 'Juan Carlos', 'Gómez Ríos', '2004-03-12', '3201110001', 'juanc.gomez@escuelaaaa.com', '1020001001', '2022-01-10'),
(2, 2, 10, 4, 'Sebastián', 'Ramírez Cruz', '2005-07-22', '3201110002', 'sebas.ramirez@escuelaaaa.com', '1020001002', '2022-01-10'),
(3, 3, 11, 4, 'Felipe', 'Castro Díaz', '2004-11-05', '3201110003', 'felipe.castro@escuelaaaa.com', '1020001003', '2022-01-10'),
(4, 4, 12, 4, 'David', 'Ospina Mejía', '2005-02-18', '3201110004', 'david.ospina2@escuelaaaa.com', '1020001004', '2022-01-10'),
(5, 5, 13, 4, 'Mateo', 'Silva Pedraza', '2004-09-30', '3201110005', 'mateo.silva@escuelaaaa.com', '1020001005', '2022-01-10'),
(6, 6, 14, 4, 'Nicolás', 'Lozano Vega', '2006-04-14', '3201110006', 'nicolas.lozano@escuelaaaa.com', '1020001006', '2022-02-01'),
(7, 7, 15, 4, 'Samuel', 'Gutiérrez Arce', '2007-08-27', '3201110007', 'samuel.gutierrez@escuelaaaa.com', '1020001007', '2022-02-01'),
(8, 8, 16, 4, 'Tomás', 'Herrera Puentes', '2006-12-01', '3201110008', 'tomas.herrera@escuelaaaa.com', '1020001008', '2022-02-01'),
(9, 9, 17, 4, 'Julián', 'Mora Sánchez', '2007-05-09', '3201110009', 'julian.mora@escuelaaaa.com', '1020001009', '2022-02-01'),
(10, 10, 18, 4, 'Andrés', 'Ruiz Patiño', '2006-10-23', '3201110010', 'andres.ruiz@escuelaaaa.com', '1020001010', '2022-02-01'),
(11, 11, 19, 4, 'Esteban', 'Jiménez Torres', '2008-01-17', '3201110011', 'esteban.jimenez@escuelaaaa.com', '1020001011', '2022-03-05'),
(12, 12, 20, 4, 'Camilo', 'Reyes Montoya', '2009-06-11', '3201110012', 'camilo.reyes@escuelaaaa.com', '1020001012', '2022-03-05'),
(13, 13, 21, 4, 'Santiago', 'Peña Córdoba', '2008-03-28', '3201110013', 'santiago.pena@escuelaaaa.com', '1020001013', '2022-03-05'),
(14, 14, 22, 4, 'Iván', 'Cardona Bernal', '2009-09-14', '3201110014', 'ivan.cardona@escuelaaaa.com', '1020001014', '2022-03-05'),
(15, 15, 23, 4, 'Alejandro', 'Flórez Vargas', '2008-07-02', '3201110015', 'alejandro.florez@escuelaaaa.com', '1020001015', '2022-03-05'),
(16, 16, 24, 4, 'José', 'Molina Quiroz', '2010-02-20', '3201110016', 'jose.molina@escuelaaaa.com', '1020001016', '2022-04-10'),
(17, 17, 25, 4, 'Manuel', 'Arango Blanco', '2011-05-15', '3201110017', 'manuel.arango@escuelaaaa.com', '1020001017', '2022-04-10'),
(18, 18, 26, 4, 'Bryan', 'Soto Niño', '2010-08-07', '3201110018', 'bryan.soto@escuelaaaa.com', '1020001018', '2022-04-10'),
(19, 19, 27, 4, 'Kevin', 'Duque Pinilla', '2011-11-19', '3201110019', 'kevin.duque@escuelaaaa.com', '1020001019', '2022-04-10'),
(20, 20, 28, 4, 'Cristian', 'León Ávila', '2010-04-03', '3201110020', 'cristian.leon@escuelaaaa.com', '1020001020', '2022-04-10'),
(21, 21, 29, 4, 'Pablo', 'Salazar Muñoz', '2014-03-11', '3201110021', 'pablo.salazar@escuelaaaa.com', '1020001021', '2022-05-15'),
(22, 22, 30, 4, 'Simón', 'Cerón Agudelo', '2015-07-25', '3201110022', 'simon.ceron@escuelaaaa.com', '1020001022', '2022-05-15'),
(23, 23, 31, 4, 'Daniel', 'Acosta Bermúdez', '2014-12-08', '3201110023', 'daniel.acosta@escuelaaaa.com', '1020001023', '2022-05-15'),
(24, 24, 32, 4, 'Matías', 'Mendoza Cano', '2015-04-17', '3201110024', 'matias.mendoza@escuelaaaa.com', '1020001024', '2022-05-15'),
(25, 25, 33, 4, 'Kevin', 'Zapata Trujillo', '2014-10-29', '3201110025', 'kevin.zapata@escuelaaaa.com', '1020001025', '2022-05-15'),
(26, NULL, 59, 4, 'luis', 'prieto', '2001-12-01', '3332224455', 'SENAprieto@CDM.com', '777', '2026-06-07'),
(27, NULL, 60, 4, 'david', 'cabezas', '2002-12-12', '3332224456', 'SENAcabezas@CDM.com', '999', '2026-06-07'),
(28, NULL, 61, 4, 'pepe', 'grillo', '2000-01-01', '3332224457', 'grillo@gmail.com', '111', '2026-06-07');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pago`
--

CREATE TABLE `pago` (
  `id_pago` int(11) NOT NULL,
  `id_jugador` int(11) NOT NULL,
  `fecha_pago` date NOT NULL,
  `monto_total` decimal(10,2) NOT NULL,
  `estado_pago` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `pago`
--

INSERT INTO `pago` (`id_pago`, `id_jugador`, `fecha_pago`, `monto_total`, `estado_pago`) VALUES
(1, 1, '2025-01-06', 75000.00, 'Pagado'),
(2, 1, '2025-02-06', 75000.00, 'Pagado'),
(3, 1, '2025-03-06', 75000.00, 'Pagado'),
(4, 2, '2025-01-07', 75000.00, 'Pagado'),
(5, 2, '2025-02-07', 75000.00, 'Pagado'),
(6, 2, '2025-03-07', 75000.00, 'Pendiente'),
(7, 3, '2025-01-08', 75000.00, 'Pagado'),
(8, 3, '2025-02-08', 75000.00, 'Pagado'),
(9, 3, '2025-03-08', 75000.00, 'Pagado'),
(10, 4, '2025-01-09', 75000.00, 'Pagado'),
(11, 4, '2025-02-09', 75000.00, 'Pendiente'),
(12, 4, '2025-03-09', 75000.00, 'Pendiente'),
(13, 5, '2025-01-05', 75000.00, 'Pagado'),
(14, 5, '2025-02-05', 75000.00, 'Pagado'),
(15, 5, '2025-03-05', 75000.00, 'Pagado'),
(16, 6, '2025-01-06', 75000.00, 'Pagado'),
(17, 6, '2025-02-06', 75000.00, 'Pagado'),
(18, 6, '2025-03-06', 75000.00, 'Pagado'),
(19, 7, '2025-01-07', 75000.00, 'Pagado'),
(20, 7, '2025-02-07', 75000.00, 'Pagado'),
(21, 7, '2025-03-07', 75000.00, 'Pagado'),
(22, 8, '2025-01-08', 75000.00, 'Pagado'),
(23, 8, '2025-02-08', 75000.00, 'Pendiente'),
(24, 8, '2025-03-08', 75000.00, 'Pendiente'),
(25, 9, '2025-01-09', 75000.00, 'Pagado'),
(26, 9, '2025-02-09', 75000.00, 'Pagado'),
(27, 9, '2025-03-09', 75000.00, 'Pagado'),
(28, 10, '2025-01-05', 75000.00, 'Pagado'),
(29, 10, '2025-02-05', 75000.00, 'Pagado'),
(30, 10, '2025-03-05', 75000.00, 'Pagado'),
(31, 11, '2025-01-06', 75000.00, 'Pagado'),
(32, 11, '2025-02-06', 75000.00, 'Pagado'),
(33, 11, '2025-03-06', 75000.00, 'Pagado'),
(34, 12, '2025-01-07', 75000.00, 'Pagado'),
(35, 12, '2025-02-07', 75000.00, 'Pagado'),
(36, 12, '2025-03-07', 75000.00, 'Pendiente'),
(37, 13, '2025-01-08', 75000.00, 'Pagado'),
(38, 13, '2025-02-08', 75000.00, 'Pagado'),
(39, 13, '2025-03-08', 75000.00, 'Pagado'),
(40, 14, '2025-01-09', 75000.00, 'Pagado'),
(41, 14, '2025-02-09', 75000.00, 'Pagado'),
(42, 14, '2025-03-09', 75000.00, 'Pagado'),
(43, 15, '2025-01-05', 75000.00, 'Pagado'),
(44, 15, '2025-02-05', 75000.00, 'Pagado'),
(45, 15, '2025-03-05', 75000.00, 'Pagado'),
(46, 16, '2025-01-06', 75000.00, 'Pagado'),
(47, 16, '2025-02-06', 75000.00, 'Pagado'),
(48, 16, '2025-03-06', 75000.00, 'Pagado'),
(49, 17, '2025-01-07', 75000.00, 'Pagado'),
(50, 17, '2025-02-07', 75000.00, 'Pendiente'),
(51, 17, '2025-03-07', 75000.00, 'Pendiente'),
(52, 18, '2025-01-08', 75000.00, 'Pagado'),
(53, 18, '2025-02-08', 75000.00, 'Pagado'),
(54, 18, '2025-03-08', 75000.00, 'Pagado'),
(55, 19, '2025-01-09', 75000.00, 'Pagado'),
(56, 19, '2025-02-09', 75000.00, 'Pagado'),
(57, 19, '2025-03-09', 75000.00, 'Pagado'),
(58, 20, '2025-01-05', 75000.00, 'Pagado'),
(59, 20, '2025-02-05', 75000.00, 'Pagado'),
(60, 20, '2025-03-05', 75000.00, 'Pagado'),
(61, 21, '2025-01-06', 75000.00, 'Pagado'),
(62, 21, '2025-02-06', 75000.00, 'Pagado'),
(63, 21, '2025-03-06', 75000.00, 'Pagado'),
(64, 22, '2025-01-07', 75000.00, 'Pagado'),
(65, 22, '2025-02-07', 75000.00, 'Pagado'),
(66, 22, '2025-03-07', 75000.00, 'Pagado'),
(67, 23, '2025-01-08', 75000.00, 'Pagado'),
(68, 23, '2025-02-08', 75000.00, 'Pagado'),
(69, 23, '2025-03-08', 75000.00, 'Pendiente'),
(70, 24, '2025-01-09', 75000.00, 'Pagado'),
(71, 24, '2025-02-09', 75000.00, 'Pagado'),
(72, 24, '2025-03-09', 75000.00, 'Pagado'),
(73, 25, '2025-01-05', 75000.00, 'Pagado'),
(74, 25, '2025-02-05', 75000.00, 'Pagado'),
(75, 25, '2025-03-05', 75000.00, 'Pagado');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `rol`
--

CREATE TABLE `rol` (
  `id_rol` int(11) NOT NULL,
  `nombre_rol` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `rol`
--

INSERT INTO `rol` (`id_rol`, `nombre_rol`) VALUES
(1, 'super_admin'),
(2, 'admin'),
(3, 'entrenador'),
(4, 'jugador'),
(5, 'acudiente');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `subdivisiones`
--

CREATE TABLE `subdivisiones` (
  `id_division` int(11) NOT NULL,
  `nombre` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `subdivisiones`
--

INSERT INTO `subdivisiones` (`id_division`, `nombre`) VALUES
(1, 'sub20'),
(2, 'sub18'),
(3, 'sub16'),
(4, 'sub14'),
(5, 'sub10');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuario`
--

CREATE TABLE `usuario` (
  `id_usuario` int(11) NOT NULL,
  `id_rol` int(11) NOT NULL,
  `usuario` varchar(50) NOT NULL,
  `contrasena` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `estado` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuario`
--

INSERT INTO `usuario` (`id_usuario`, `id_rol`, `usuario`, `contrasena`, `email`, `estado`) VALUES
(1, 1, 'sebastianADMIN', '1234', 'sebastian.camargo@escuelaaaa.com', 'activo'),
(2, 1, 'alexander_acevedo', 'hashed_pass_SA2', 'alexander.acevedo@escuelaaaa.com', 'activo'),
(3, 2, 'admin_escuela', 'hashed_pass_002', 'admin@escuelaaaa.com', 'activo'),
(4, 3, 'ent_delanteros', 'hashed_pass_003', 'carlos.rios@escuelaaaa.com', 'activo'),
(5, 3, 'ent_mediocampis', 'hashed_pass_004', 'jorge.mendez@escuelaaaa.com', 'activo'),
(6, 3, 'ent_defensas', 'hashed_pass_005', 'andres.vargas@escuelaaaa.com', 'activo'),
(7, 3, 'ent_porteros', 'hashed_pass_006', 'luis.perez@escuelaaaa.com', 'activo'),
(8, 3, 'ent_general', 'hashed_pass_007', 'miguel.torres@escuelaaaa.com', 'activo'),
(9, 4, 'jug_s20_001', 'hashed_pass_008', 'juanc.gomez@escuelaaaa.com', 'activo'),
(10, 4, 'jug_s20_002', 'hashed_pass_009', 'sebas.ramirez@escuelaaaa.com', 'activo'),
(11, 4, 'jug_s20_003', 'hashed_pass_010', 'felipe.castro@escuelaaaa.com', 'activo'),
(12, 4, 'jug_s20_004', 'hashed_pass_011', 'david.ospina2@escuelaaaa.com', 'activo'),
(13, 4, 'jug_s20_005', 'hashed_pass_012', 'mateo.silva@escuelaaaa.com', 'activo'),
(14, 4, 'jug_s18_001', 'hashed_pass_013', 'nicolas.lozano@escuelaaaa.com', 'activo'),
(15, 4, 'jug_s18_002', 'hashed_pass_014', 'samuel.gutierrez@escuelaaaa.com', 'activo'),
(16, 4, 'jug_s18_003', 'hashed_pass_015', 'tomas.herrera@escuelaaaa.com', 'activo'),
(17, 4, 'jug_s18_004', 'hashed_pass_016', 'julian.mora@escuelaaaa.com', 'activo'),
(18, 4, 'jug_s18_005', 'hashed_pass_017', 'andres.ruiz@escuelaaaa.com', 'activo'),
(19, 4, 'jug_s16_001', 'hashed_pass_018', 'esteban.jimenez@escuelaaaa.com', 'activo'),
(20, 4, 'jug_s16_002', 'hashed_pass_019', 'camilo.reyes@escuelaaaa.com', 'activo'),
(21, 4, 'jug_s16_003', 'hashed_pass_020', 'santiago.pena@escuelaaaa.com', 'activo'),
(22, 4, 'jug_s16_004', 'hashed_pass_021', 'ivan.cardona@escuelaaaa.com', 'activo'),
(23, 4, 'jug_s16_005', 'hashed_pass_022', 'alejandro.florez@escuelaaaa.com', 'activo'),
(24, 4, 'jug_s14_001', 'hashed_pass_023', 'jose.molina@escuelaaaa.com', 'activo'),
(25, 4, 'jug_s14_002', 'hashed_pass_024', 'manuel.arango@escuelaaaa.com', 'activo'),
(26, 4, 'jug_s14_003', 'hashed_pass_025', 'bryan.soto@escuelaaaa.com', 'activo'),
(27, 4, 'jug_s14_004', 'hashed_pass_026', 'kevin.duque@escuelaaaa.com', 'activo'),
(28, 4, 'jug_s14_005', 'hashed_pass_027', 'cristian.leon@escuelaaaa.com', 'activo'),
(29, 4, 'jug_s10_001', 'hashed_pass_028', 'pablo.salazar@escuelaaaa.com', 'activo'),
(30, 4, 'jug_s10_002', 'hashed_pass_029', 'simon.ceron@escuelaaaa.com', 'activo'),
(31, 4, 'jug_s10_003', 'hashed_pass_030', 'daniel.acosta@escuelaaaa.com', 'activo'),
(32, 4, 'jug_s10_004', 'hashed_pass_031', 'matias.mendoza@escuelaaaa.com', 'activo'),
(33, 4, 'jug_s10_005', 'hashed_pass_032', 'kevin.zapata@escuelaaaa.com', 'activo'),
(34, 5, 'acu_001', 'hashed_pass_033', 'padre.gomez@gmail.com', 'activo'),
(35, 5, 'acu_002', 'hashed_pass_034', 'madre.ramirez@gmail.com', 'activo'),
(36, 5, 'acu_003', 'hashed_pass_035', 'padre.castro@gmail.com', 'activo'),
(37, 5, 'acu_004', 'hashed_pass_036', 'madre.ospina@gmail.com', 'activo'),
(38, 5, 'acu_005', 'hashed_pass_037', 'tutor.silva@gmail.com', 'activo'),
(39, 5, 'acu_006', 'hashed_pass_038', 'padre.lozano@gmail.com', 'activo'),
(40, 5, 'acu_007', 'hashed_pass_039', 'madre.gutierrez@gmail.com', 'activo'),
(41, 5, 'acu_008', 'hashed_pass_040', 'padre.herrera@gmail.com', 'activo'),
(42, 5, 'acu_009', 'hashed_pass_041', 'madre.mora@gmail.com', 'activo'),
(43, 5, 'acu_010', 'hashed_pass_042', 'tutor.ruiz@gmail.com', 'activo'),
(44, 5, 'acu_011', 'hashed_pass_043', 'padre.jimenez@gmail.com', 'activo'),
(45, 5, 'acu_012', 'hashed_pass_044', 'madre.reyes@gmail.com', 'activo'),
(46, 5, 'acu_013', 'hashed_pass_045', 'padre.pena@gmail.com', 'activo'),
(47, 5, 'acu_014', 'hashed_pass_046', 'madre.cardona@gmail.com', 'activo'),
(48, 5, 'acu_015', 'hashed_pass_047', 'tutor.florez@gmail.com', 'activo'),
(49, 5, 'acu_016', 'hashed_pass_048', 'padre.molina@gmail.com', 'activo'),
(50, 5, 'acu_017', 'hashed_pass_049', 'madre.arango@gmail.com', 'activo'),
(51, 5, 'acu_018', 'hashed_pass_050', 'padre.soto@gmail.com', 'activo'),
(52, 5, 'acu_019', 'hashed_pass_051', 'madre.duque@gmail.com', 'activo'),
(53, 5, 'acu_020', 'hashed_pass_052', 'tutor.leon@gmail.com', 'activo'),
(54, 5, 'acu_021', 'hashed_pass_053', 'padre.salazar@gmail.com', 'activo'),
(55, 5, 'acu_022', 'hashed_pass_054', 'madre.ceron@gmail.com', 'activo'),
(56, 5, 'acu_023', 'hashed_pass_055', 'padre.acosta@gmail.com', 'activo'),
(57, 5, 'acu_024', 'hashed_pass_056', 'madre.mendoza@gmail.com', 'activo'),
(58, 5, 'acu_025', 'hashed_pass_057', 'tutor.zapata@gmail.com', 'activo'),
(59, 4, '777', '666', '', 'Activo'),
(60, 4, '999', '888', '', 'Activo'),
(61, 4, '111', '222', 'grillo@gmail.com', 'Activo');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `acudiente`
--
ALTER TABLE `acudiente`
  ADD PRIMARY KEY (`id_acudiente`),
  ADD KEY `id_usuario` (`id_usuario`),
  ADD KEY `id_rol` (`id_rol`);

--
-- Indices de la tabla `asistencia`
--
ALTER TABLE `asistencia`
  ADD PRIMARY KEY (`id_asistencia`),
  ADD KEY `id_entrenamiento` (`id_entrenamiento`),
  ADD KEY `id_jugador` (`id_jugador`),
  ADD KEY `id_equipo` (`id_equipo`);

--
-- Indices de la tabla `detalle_pago`
--
ALTER TABLE `detalle_pago`
  ADD PRIMARY KEY (`id_detalle`),
  ADD KEY `id_pago` (`id_pago`);

--
-- Indices de la tabla `entrenador`
--
ALTER TABLE `entrenador`
  ADD PRIMARY KEY (`id_entrenador`),
  ADD KEY `id_usuario` (`id_usuario`),
  ADD KEY `id_rol` (`id_rol`);

--
-- Indices de la tabla `entrenamiento`
--
ALTER TABLE `entrenamiento`
  ADD PRIMARY KEY (`id_entrenamiento`),
  ADD KEY `id_entrenador` (`id_entrenador`),
  ADD KEY `id_equipo` (`id_equipo`);

--
-- Indices de la tabla `equipo`
--
ALTER TABLE `equipo`
  ADD PRIMARY KEY (`id_equipo`),
  ADD KEY `id_division` (`id_division`);

--
-- Indices de la tabla `estado_jugador`
--
ALTER TABLE `estado_jugador`
  ADD PRIMARY KEY (`id_estado`);

--
-- Indices de la tabla `ficha_jugador`
--
ALTER TABLE `ficha_jugador`
  ADD PRIMARY KEY (`id_jugador`),
  ADD KEY `id_equipo` (`id_equipo`),
  ADD KEY `id_estado` (`id_estado`);

--
-- Indices de la tabla `jugador`
--
ALTER TABLE `jugador`
  ADD PRIMARY KEY (`id_jugador`),
  ADD KEY `id_acudiente` (`id_acudiente`),
  ADD KEY `id_usuario` (`id_usuario`),
  ADD KEY `id_rol` (`id_rol`);

--
-- Indices de la tabla `pago`
--
ALTER TABLE `pago`
  ADD PRIMARY KEY (`id_pago`),
  ADD KEY `id_jugador` (`id_jugador`);

--
-- Indices de la tabla `rol`
--
ALTER TABLE `rol`
  ADD PRIMARY KEY (`id_rol`);

--
-- Indices de la tabla `subdivisiones`
--
ALTER TABLE `subdivisiones`
  ADD PRIMARY KEY (`id_division`);

--
-- Indices de la tabla `usuario`
--
ALTER TABLE `usuario`
  ADD PRIMARY KEY (`id_usuario`),
  ADD KEY `id_rol` (`id_rol`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `acudiente`
--
ALTER TABLE `acudiente`
  MODIFY `id_acudiente` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=26;

--
-- AUTO_INCREMENT de la tabla `jugador`
--
ALTER TABLE `jugador`
  MODIFY `id_jugador` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=29;

--
-- AUTO_INCREMENT de la tabla `usuario`
--
ALTER TABLE `usuario`
  MODIFY `id_usuario` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=62;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `acudiente`
--
ALTER TABLE `acudiente`
  ADD CONSTRAINT `acudiente_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`),
  ADD CONSTRAINT `acudiente_ibfk_2` FOREIGN KEY (`id_rol`) REFERENCES `rol` (`id_rol`);

--
-- Filtros para la tabla `asistencia`
--
ALTER TABLE `asistencia`
  ADD CONSTRAINT `asistencia_ibfk_1` FOREIGN KEY (`id_entrenamiento`) REFERENCES `entrenamiento` (`id_entrenamiento`),
  ADD CONSTRAINT `asistencia_ibfk_2` FOREIGN KEY (`id_jugador`) REFERENCES `jugador` (`id_jugador`),
  ADD CONSTRAINT `asistencia_ibfk_3` FOREIGN KEY (`id_equipo`) REFERENCES `equipo` (`id_equipo`);

--
-- Filtros para la tabla `detalle_pago`
--
ALTER TABLE `detalle_pago`
  ADD CONSTRAINT `detalle_pago_ibfk_1` FOREIGN KEY (`id_pago`) REFERENCES `pago` (`id_pago`);

--
-- Filtros para la tabla `entrenador`
--
ALTER TABLE `entrenador`
  ADD CONSTRAINT `entrenador_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`),
  ADD CONSTRAINT `entrenador_ibfk_2` FOREIGN KEY (`id_rol`) REFERENCES `rol` (`id_rol`);

--
-- Filtros para la tabla `entrenamiento`
--
ALTER TABLE `entrenamiento`
  ADD CONSTRAINT `entrenamiento_ibfk_1` FOREIGN KEY (`id_entrenador`) REFERENCES `entrenador` (`id_entrenador`),
  ADD CONSTRAINT `entrenamiento_ibfk_2` FOREIGN KEY (`id_equipo`) REFERENCES `equipo` (`id_equipo`);

--
-- Filtros para la tabla `equipo`
--
ALTER TABLE `equipo`
  ADD CONSTRAINT `equipo_ibfk_1` FOREIGN KEY (`id_division`) REFERENCES `subdivisiones` (`id_division`);

--
-- Filtros para la tabla `ficha_jugador`
--
ALTER TABLE `ficha_jugador`
  ADD CONSTRAINT `ficha_jugador_ibfk_1` FOREIGN KEY (`id_jugador`) REFERENCES `jugador` (`id_jugador`),
  ADD CONSTRAINT `ficha_jugador_ibfk_2` FOREIGN KEY (`id_equipo`) REFERENCES `equipo` (`id_equipo`),
  ADD CONSTRAINT `ficha_jugador_ibfk_3` FOREIGN KEY (`id_estado`) REFERENCES `estado_jugador` (`id_estado`);

--
-- Filtros para la tabla `jugador`
--
ALTER TABLE `jugador`
  ADD CONSTRAINT `jugador_ibfk_1` FOREIGN KEY (`id_acudiente`) REFERENCES `acudiente` (`id_acudiente`),
  ADD CONSTRAINT `jugador_ibfk_2` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`),
  ADD CONSTRAINT `jugador_ibfk_3` FOREIGN KEY (`id_rol`) REFERENCES `rol` (`id_rol`);

--
-- Filtros para la tabla `pago`
--
ALTER TABLE `pago`
  ADD CONSTRAINT `pago_ibfk_1` FOREIGN KEY (`id_jugador`) REFERENCES `jugador` (`id_jugador`);

--
-- Filtros para la tabla `usuario`
--
ALTER TABLE `usuario`
  ADD CONSTRAINT `usuario_ibfk_1` FOREIGN KEY (`id_rol`) REFERENCES `rol` (`id_rol`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
