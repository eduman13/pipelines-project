# Homenaje a Kobe Bryant
## Introducción
El pasado 26 de Febrero de 2020 nos dejaba el exjugador de Los Angeles Lakers Kobe Bryant en un fatidico accidente de helicóptero. Como muchos chicos de mi generación amantes del baloncesto crecimos viendo sus espectaculares movimientos, canastas y actuaciones. Por eso quiero dedicarle este pequeño script a su memoria

![Kobe Bryant](/Imagenes/kobeBryant.jpg)

## Descripción
El programa muestra las estadísticas de tres de los mejores jugadores de la historia de la NBA: Kobe Bryant, LeBron James y Michael Jordan, para intentar aclarar quien es el mejor de los tres aunque para gusto los colores.

## Flags
-h: Muestra la ayuda
--name=NAME: Este flag que admite un valor, que puede ser: kobe, lebron o jordan, nos mostrará las estadísticas relacionadas con el jugador indicado
--playoffs: Este flag nos mostrará las estadísticas de playoffs del jugador seleccionado
-c: Este flag nos mostrará las estadísticas de los años en que los jugadores ganaron el campeonato de la NBA
-m: Este flag nos mostrará las estadísticas de los años donde los jugadores ganaron el MVP (Most Valuable Player)
<b>Nota:</b> Los flags -c y -m no pueden ponerse a la vez
-graph: Este flag nos muestra un gráfico con las estadísticas de los tres jugadores
--mailto=EMAIL: Envía el gráfico generado con el flag --graph al email indicado (solo permite uno)
