# P2_Puente
El objetivo de la práctica trata de garantizar una coordinación entre distintos procesos para poder atravesar un puente. A la hora de cruzar el puente podemos encontrarnos distintos procesos: peatones, coches que van hacia el sur y coches que van hacia el norte. No pueden estar procesos de distintos tipos en el puente a la vez, es decir, es necesario garantizar la exclusión mutua, además querremos evitar deadlock. Para la resolución de este problema vamos a hacer uso de monitores para el acceso a la entrada al puente. Hemos planteado dos soluciones:   

La primera garantiza exclusión mutua y libre de deadlock, pero existe inanición: p2_conInanicion.py  

La segunda garantiza exclusión mutua, libre de deadlock y libre de inanición: p2.py

Finalmente, hemos añadido un pdf con las demostraciones necesarias para la comprobación de las anteriores condiciones: p2_dems.pdf
