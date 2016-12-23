Descripcion:

Dentro de la carpeta scripts se encuentran los programas ejecutables 
mediante los cuales se ejecuta el modelo en su version operacional
Dentro de esta carpeta se encuetran los siguientes scripts:

- Cron_Actualiza_Campo.py:

	Actualiza al ultimo campo de radar, convierte reflectividad 
	a lluvia mediante la tranformacion de Julian 2015.
	#####
	Llama a: GeneraCampos_v2.py
        ####
        Utiliza a:
                - /home/renea998/binCuencas/cuencaAMVA_vYY.nc
                - /mnt/RADAR/reprojected_data/


- Cron_Campo_olver.py:

	Toma las imagenes extrapoladas de Olver, localizadas en:
	/mnt/RADAR/extrapolated/ y genera el binario para simulacion 
	con las ultimas 24 extrapolaciones.
	#####
	Llama a: GeneraCampos_Olver.py
	####
	Utiliza a:
		- /home/renea998/binCuencas/cuencaAMVA_vYY.nc
		- /mnt/RADAR/extrapolation/

- Cron_Ejecucion_Modelo.py:

	Ejecuta el modelo cada 5min tomando la ultima imagen actual 
	y las 24 imagenes de olver.
	####
	Llama a: Ejecuta_Modelo_v2.py
	####
	Utiliza:
		- /home/renea998/binCuencas/cuencaAMVA_vYY.nc
		- /mnt/RADAR/CamposNicolas/Campo_AMVA_operacional3
		- /mnt/RADAR/CAmposNicolas/Campo_AMVA_extrapolated

- Cron_Figura_SimSimple.py:

	Genera Figuras aleatorias de los 290 nodos de la red hidrica 
	del valle de aburra.
	####
	Llama a:
		- Figuras_Qsim.py
	####
	Utiliza a:
		- /home/renea998/Simulaciones/
		- Qsim_cu01_Calib_01_hist.qsim

