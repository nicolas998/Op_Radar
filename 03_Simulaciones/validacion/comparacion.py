import MySQLdb
import matplotlib
matplotlib.use('Agg')
import numpy as np
import pylab as pl
import cPickle
import numpy.ma as ma
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import datetime as dt
import math
import os
import sys, getopt

path='/home/renea998/Simulaciones/'
config='0'+sys.argv[1]
date_ini=dt.datetime(int(sys.argv[2].split('-')[0]),int(sys.argv[2].split('-')[1]),int(sys.argv[2].split('-')[2]),int(sys.argv[3].split(':')[0]),int(sys.argv[3].split(':')[1]))
date_fin=dt.datetime(int(sys.argv[4].split('-')[0]),int(sys.argv[4].split('-')[1]),int(sys.argv[4].split('-')[2]),int(sys.argv[5].split(':')[0]),int(sys.argv[5].split(':')[1]))
guardar=sys.argv[6]

col=['r','g','k']
arch=os.listdir(path)
num_cal=[]
rezago=[0,0]
for rr in arch:
	try:
		if rr.split('_')[1] == 'cu'+config:
			num_cal.append(int(rr.split('_')[3]))
	except:
		pass

#parametros de las estaciones
par_pto=np.genfromtxt(path+'/validacion/puntos_control.txt', delimiter='	', dtype=str)
offset1=[] ; est_N1=[] ; exp_curva1=[] ; coe_curva1=[] ; nodo1=[]

for l in par_pto:
	nodo1.append(int(l[0]))
	est_N1.append(float(l[1]))
	offset1.append(float(l[2]))
        exp_curva1.append(float(l[3]))
        coe_curva1.append(float(l[4]))

#funciones para evaluar eficiencia

def eval_nash(s_o,s_s):
    med_s_o=np.nansum(s_o)/np.sum(np.isfinite(s_o))
    Dif_sim=(s_o-s_s[:len(s_o)])**2
    Dif_med=(s_o-med_s_o)**2
    E=1-(np.nansum(Dif_sim)/np.nansum(Dif_med))
    return E

def eval_q_pico(s_o,s_s):
    max_o=np.argmax(np.ma.array(s_o,mask=np.isnan(s_o)))
    max_s=np.argmax(np.ma.array(s_s,mask=np.isnan(s_s)))
    Qo_max=s_o[max_o]
    Qs_max=s_s[max_s]
    dif_qpico=((Qo_max-Qs_max)/Qo_max)*100
    return dif_qpico

def eval_t_pico(s_o,s_s,dt):
    max_o=np.argmax(np.ma.array(s_o,mask=np.isnan(s_o)))
    max_s=np.argmax(np.ma.array(s_s,mask=np.isnan(s_s)))
    dif_tpico=(max_o-max_s)*dt
    return dif_tpico

def eval_vol(s_o,s_s):
    vol_o=np.nansum(s_o)*360.
    vol_s=np.nansum(s_s)*360.
    dif_vol=((vol_o-vol_s)/vol_o)*100
    return dif_vol

for nod in range(len(nodo1)):

	fig=plt.figure(edgecolor='w',facecolor='w',figsize=(12,9))
	ax=fig.add_subplot(1,1,1)

	for calib in num_cal:

		flag_his=0
		nodo=nodo1[nod]
		# leer caudales simulados
		f=open(path+'Qsim_cu'+config+'_Calib_0'+str(calib)+'_hist.qsim','r')
		Qsim=cPickle.load(f)
		f.close()
		file=Qsim[nodo]
		ndatos=len(file)
		date_index=[] ; Q_values=[]
		for t in range(len(file.index)):
			date_index.append(dt.datetime(file.index[t].year,file.index[t].month,file.index[t].day,file.index[t].hour,file.index[t].minute))
			Q_values.append(file.values[t])
		nn=np.where(np.array(date_index) >= date_ini)[0]
		mm=np.where(np.array(date_index) <= date_fin)[0]
		qq=celdas_sub=list(set(nn).intersection(mm))
		date_caudal=np.array(date_index)[qq]
		Qs=np.array(Q_values)[qq]

		year=date_ini.year ; month=date_ini.month ; day=date_ini.day ; hour=date_ini.hour ; minute=date_ini.minute
		if nodo < 10:
        		nodo='0'+str(nodo)
		if month < 10:
			month='0'+str(month)
		if day < 10:
			day='0'+str(day)
		if hour < 10:
                        hour='0'+str(hour)
		if minute < 10:
                        minute='0'+str(minute)
		try:
			historico=np.genfromtxt(path+'/validacion/Eficiencia_N'+str(nodo)+'_Conf'+config+'_C'+str(calib)+'.txt',delimiter='	', dtype=str)
			flag_his=1
		except:
			pass
		
		# parametros de la estacion
		offset=offset1[nod]
		est_N=est_N1[nod]
		exp_curva=exp_curva1[nod]
		coe_curva=coe_curva1[nod]

		# open database connection
		host      ='192.168.1.74'
		user      ='usrCalidad'
		passw     ='aF05wnXC;'
		bd_nombre ='siata'
	
		if calib == 1:
			datos_p = "SELECT DATE_FORMAT(fecha,'%Y-%m-%d'), DATE_FORMAT(hora, '%H:%i:%s') ,("+str(offset)+"-Ni),calidad FROM datos WHERE cliente = "+str(est_N)+" and calidad='1' and (((fecha>'"+str(date_ini.year)+"-"+str(date_ini.month)+"-"+str(date_ini.day)+"') or (fecha='"+str(date_ini.year)+"-"+str(date_ini.month)+"-"+str(date_ini.day)+"' and hora>='"+str(date_ini.hour)+":"+str(date_ini.minute)+":00')) and ((fecha<'"+str(date_fin.year)+"-"+str(date_fin.month)+"-"+str(date_fin.day)+"') or (fecha='"+str(date_fin.year)+"-"+str(date_fin.month)+"-"+str(date_fin.day)+"' and hora<='"+str(date_fin.hour)+":"+str(date_fin.minute)+":00')))"
			db = MySQLdb.connect(host, user,passw,bd_nombre)
			db_cursor = db.cursor()
			db_cursor.execute(datos_p)
			data = db_cursor.fetchall()

			date_nivel=[] ; N=[] ; Qobs=[] 
			print nodo
			for i in range(len(data)):
				if data[i][3] < 100:
					date_nivel.append(dt.datetime(int(data[i][0].split('-')[0]),int(data[i][0].split('-')[1]),int(data[i][0].split('-')[2]),int(data[i][1].split(':')[0]),int(data[i][1].split(':')[1]),int(data[i][1].split(':')[2])) + dt.timedelta(minutes=rezago[nod]))
					N.append(float(data[i][2]))
					Qobs.append(coe_curva*(float(data[i][2])/100.)**(exp_curva))

			Qob5=[]

			for k in date_caudal:
			
				dd=np.where(np.array(date_nivel) >= k-dt.timedelta(minutes=2))[0]
				ee=np.where(np.array(date_nivel) <= k+dt.timedelta(minutes=2))[0]
				ff=list(set(dd).intersection(ee))
				Qob5.append(np.mean(np.array(Qobs)[ff]))

			#plt.plot(np.array(date_nivel),np.array(Qobs),color='g',label='Observado')
			plt.plot(np.array(date_caudal),np.array(Qob5),color='b',label='Observado',lw=2)
		Nash=eval_nash(np.array(Qob5),np.array(Qs))
		print Qob5
		print Qs
		Qpico=eval_q_pico(np.array(Qob5),np.array(Qs))
		Tpico=eval_t_pico(np.array(Qob5),np.array(Qs),5)
		Dvol=eval_vol(np.array(Qob5),np.array(Qs))
		evento=[]

		if guardar=='S':
			if flag_his==1:
				try:
					historico.shape[1]
					tamanho=historico.shape[0]
					for j in range(tamanho):
                                        	evento.append(historico[j][0]+'	'+historico[j][1]+'	'+historico[j][2]+'	'+historico[j][3]+'	'+historico[j][4]+'	'+historico[j][5]+'	'+historico[j][6])
				except:
					tamanho=1
					evento.append(historico[0]+'	'+historico[1]+'	'+historico[2]+'	'+historico[3]+'	'+historico[4]+'	'+historico[5]+'	'+historico[6])

			evento.append(str(year)+'-'+str(month)+'-'+str(day)+'	'+str(hour)+':'+str(minute)+'	'+str(Nash)+'	'+str(Qpico)+'	'+str(Tpico)+'	'+str(Dvol)+'	'+str(np.nanmax(Qob5)))
			np.savetxt('Eficiencia_N'+str(nodo)+'_Conf'+config+'_C'+str(calib)+'.txt',evento,fmt="%s")
		plt.plot(np.array(date_caudal),np.array(Qs),color=col[calib-1],label='Calib '+str(calib),lw=2) #+': Na='+ "%.2f" % Nash+', Qp='+ "%.1f" % Qpico+'%, Vol='+ "%.1f" % Dvol+'%, Tp='+ "%.0f" % Tpico+' min')

	plt.grid()
	plt.legend()
	formatter = DateFormatter('%b-%d\n%H:%M')
	ax.xaxis.set_major_formatter(formatter)
	plt.title("Nodo:"+str(nodo)+" "+str(year)+"-"+str(month)+"-"+str(day))
	plt.xlabel('$Tiempo$',fontsize=18)
	plt.ylabel('$Caudal$ $[m^{3}/s]$',fontsize=18)
	#plt.ylim(10,200)
	plt.savefig('comparacion_'+str(nodo)+'.png')
	os.system("scp /home/renea998/Simulaciones/validacion/comparacion_"+str(nodo)+".png torresiata@192.168.1.74:/var/www/nicolas/Validacion/Fig_Hidrografas/QvsS_N"+str(nodo)+"_Conf"+config+"_"+str(year)+str(month)+str(day)+".png")
