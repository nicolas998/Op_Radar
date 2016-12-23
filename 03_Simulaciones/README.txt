En esta carpeta se encuentran los caudales simulados para le cuenca del AMVA
en cada uno de los nodos hidrologicos determinados por el modelo (alrededor de 290)
en la carpeta raiz se encuentran los archivos:

-----------------------------------------------------------------------------------
Qsim_cuYY_Calib_XX_hist.qsim

Estos son archivos historicos de simulaciones de caudal y son utilizados para 
comparaciones y de los modelos en el pasado.

YY: numero de configuracion de la cuenca.
XX: numero de calibracion de la configuracion

-------------------------------------------------------------------------------------
Qsim_cuYY_Calib_XX.qsim

Simulaciones de los ultimos 5 minutos de modelacion, se usan para 
actualizar registros en Qsim_cuYY_Calib_XX_hist.qsim y para generar figuras 
de simulacion

---------------------------------------------------------------------------------
Qsim_ext_cuYY_Calib_XX.qsim

Simulaciones de las extrapolaciones de 2 horas adelante utilizando los campos
generados por Olver.

-----------------------------------------------------------------------------


