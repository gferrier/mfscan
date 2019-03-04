#!/home/palandir/.conda/envs/aliscan/bin/python
import urllib.request
import urllib.parse
import re
import psycopg2
from datetime import datetime
import time


try:
	conn = psycopg2.connect(dbname='lgbd', user='palandir', host='localhost', password='palandir')
	cur = conn.cursor()
except psycopg2.Error as e:
#except:
	print("I am unable to connect to the database")
	print(e.pgerror)
	print(e)

cur.execute("""select a.id,a.aliname,c.latestimg from alistores a inner join alistoretoparse b on a.id=b.id left outer join alilastscan c on a.id=c.idstore""")
# TBD ajouter la generation auto des url selon aliurlgen

for storeid,storename,oldlatestimg in cur.fetchall():
	url = 'https://fr.aliexpress.com/store/new-arrivals/3904022.html?origin=n&SortType=new_desc&page=2'
	#https://fr.aliexpress.com/store/new-arrivals/1952643.html?origin=n&SortType=new_desc'
	#https://worldminifigures.fr.aliexpress.com/store/new-arrivals/1041264.html?origin=n&SortType=new_desc'
	#https://fr.aliexpress.com/store/new-arrivals/3904022.html?origin=n&SortType=new_desc'
	#url = 'https://fr.aliexpress.com/store/group/Star-wars/3904022_513320934/6.html?spm=a2g0w.12010612.8148361.6.6cde16430daqOV&origin=n&SortType=new_desc&g=y'
	#url = 'https://fr.aliexpress.com/store/all-wholesale-products/'+str(storeid)+'.html?SortType=new_desc'#&page=2'
	#url = 'https://fr.aliexpress.com/store/new-arrivals/'+str(storeid)+'.html?SortType=new_desc'
	#url = 'https://fr.aliexpress.com/store/new-arrivals/3904022.html?origin=n&SortType=new_desc'
	#url = 'https://fr.aliexpress.com/store/new-arrivals/2006008.html?origin=n&SortType=new_desc'
	#url = 'https://worldminifigures.fr.aliexpress.com/store/new-arrivals/1041264.html?SortType=new_desc&page=2'
	#url = 'https://fr.aliexpress.com/store/new-arrivals/3628010.html?origin=n&SortType=new_desc'
	# NB SYNTAX	
	#cur.execute(sql, (value1,value2))
	#cur.executemany(sql,vendor_list)
	#
	#You pass the INSERT statement to the first parameter and a list of values to the second parameter of the execute() method.
	#
	#In case the primary key of the table is an auto-generated column, you can get the generated ID back after inserting the row. To do this, in the INSERT statement, you use the RETURNING id clause. After calling the execute() method, you call the  fetchone() method of the cursor object to get the id value as follows:
	#id = cur.fetchone()[0]
	#
	#After that, call the commit() method of the connection object to save the changes to the database permanently. If you forget to call the commit() method, psycopg will not change anything to the database.
	#conn.commit()
	
	# FONCTION OU PROC STOCK
	#cur.callproc(‘stored_procedure_name’, (value1,value2))
	#Internally, the  callproc() method translates the stored procedure call and input values into the following statement:
	#SELECT * FROM stored_procedure_name(value1,value2);
	#Therefore, you can use the execute() method of the cursor object to call a stored procedure as follows:
	#cur.execute("SELECT * FROM stored_procedure_name( %s,%s); ",(value1,value2))
	#After that, process the result set returned by the stored procedure using the fetchone(),  fetchall(), or  fetchmany() method.
	
	#row = cur.fetchone()
	#while row is not None:
	#	print(row)
	#	row = cur.fetchone()
	#        # close the communication with the PostgreSQL database server
	#        cur.close()
	#    except (Exception, psycopg2.DatabaseError) as error:
	#        print(error)
	#    finally:
	#        if conn is not None:
	#            conn.close()
	
	#values = {'s':'basics','submit':'search'} # dictionnaire a renvoyer en variables POST ? &var=val
	#data = urllib.parse.urlencode(values).encode('utf-8')
	#req  = urllib.request.Request(url,data)
	#resp = urllib.request.urlopen(req)
	#respData = resp.read()
	
	respData = urllib.request.urlopen(urllib.request.Request(url)).read()
	
	# les vignettes de la splashpage : tuple lien_item, image, label_as_alt
	patternPageStore = r'<a class="pic-rind" href="([^"]*?)" ><img class="picCore lazy-load" image-src="([^"]*?)_200.200.jpg" alt="([^"]*?)"'

	# une page et son contenu :
	# le title long de la page/objet
	patternItemFullName = r'<h1 class="product-name"[^>]*?>([^<]*?)<)'

	# les vignettes à droite de "couleur" : tuple label_mini, image
	patternItemTopRight = r'<li class="item-sku-image .* title="([^"]*?)".*<img src="([^"]*?)_50x50.jpg"'

	# l objet et ses illustrations en menu de gauche : tuple image
	#(TBD voir pour la frame ajax plus tard)
	patternItemLeftMenu = r'<li><span class="img-thumb-item">.*?src="([^"]*?)_50x50.jpg"'

	# NB parentheses capturantes pour recuperer dans le tuple de sortie
	# * est greedy donc lui preferer *?
	
	# recup de la page
	respData = urllib.request.urlopen(urllib.request.Request(url)).read()
	# recherche des motifs des images/liens
	motifsIdents = re.findall( patternPageStore, str(respData) )
	# NB en mode compile ... re.compile('name (.*) is valid').findall(datalines)
	
	print(len(motifsIdents))
	
	newlatestimg = None
	
	# On regarde toutes les images
	for href,imgid,label in motifsIdents:
		time.sleep( 2 )
		href = 'https:'+href 
		imgid = 'https:'+imgid
		
		# extraction nom image # TBD voir si possible a integrer dans le motif initial ...
		bozo = re.search(r'/kf/([^/]*?)/',imgid).group(1)
	
		# on stocke la premiere image pour archiver plus tard comme la plus recente de la boutique
		if newlatestimg is None:
			newlatestimg = str(bozo)
	
		# si on est deja comme la derniere img commue de la boutique on a fini
		if bozo == oldlatestimg:
			print('fin des images nouvelles')
			break
	
		#Sinon on va processer ce lien/Image
		#Verif que existe pas deja
		cur.execute("""SELECT count(1) FROM aliimgscanned WHERE latestimg = %s LIMIT 1""",(bozo,))
		nbexist, = cur.fetchone()
		if nbexist > 0:
			print('img splash deja en base')
		else:
			print('img splash pas en base on stocke')
			#TBD ajouter le parse de la page pour l'instant version 1 on stocke deja l'img elle meme...
			with open(bozo + '.jpg' , "wb") as f:
				f.write(urllib.request.urlopen(urllib.request.Request(imgid)).read())
			cur.execute("""INSERT into aliimgscanned ( scandate , idstore , latestimg , shorttitle , longtitle , minilabel ) VALUES (
				%s, %s, %s, %s, %s, %s )""",(datetime.now(),storeid, bozo, label[:100], label[:200], label[:50]))
		# TMP dans tous les cas
		# recup de la page de l'item
# TBD RABBIT HOLE cookie et indent
#		respDatPag = urllib.request.urlopen(urllib.request.Request(href)).read()
#		print('DEBUG item ', href,' size ',len(respDatPag))
#		motifsIdsItemRight = re.findall( patternItemTopRight, str(respDatPag) )
#		motifsIdsItemLeft = re.findall( patternItemLeftMenu, str(respDatPag) )
#		print('DEBUG ',len(motifsIdsItemRight), ' Right ', len(motifsIdsItemLeft), ' Left')
#
#		for imgiditl in motifsIdsItemLeft:
#			bozo = re.search(r'/kf/([^/]*?)/',imgiditl).group(1)
#			cur.execute("""SELECT count(1) FROM aliimgscanned WHERE latestimg = %s LIMIT 1""",(bozo,))
#			nbexist, = cur.fetchone()
#			if nbexist > 0:
#				print('img left deja en base')
#			else:
#				time.sleep( 2 )
#				print('img left pas en base on stocke')
#				with open(bozo + '.jpg' , "wb") as f:
#					f.write(urllib.request.urlopen(urllib.request.Request(imgiditl)).read())
#				cur.execute("""INSERT into aliimgscanned ( scandate , idstore , latestimg , shorttitle , longtitle , minilabel ) VALUES (
#					%s, %s, %s, %s, %s, %s )""",(datetime.now(),storeid, bozo, label[:100], label[:200], label[:50]))
#		for labelmini,imgiditr in motifsIdsItemRight:
#			bozo = re.search(r'/kf/([^/]*?)/',imgiditr).group(1)
#			cur.execute("""SELECT count(1) FROM aliimgscanned WHERE latestimg = %s LIMIT 1""",(bozo,))
#			nbexist, = cur.fetchone()
#			if nbexist > 0:
#				print('img right deja en base')
#			else:
#				time.sleep( 2 )
#				print('img right pas en base on stocke')
#				with open(bozo + '.jpg' , "wb") as f:
#					f.write(urllib.request.urlopen(urllib.request.Request(imgiditr)).read())
#				cur.execute("""INSERT into aliimgscanned ( scandate , idstore , latestimg , shorttitle , longtitle , minilabel ) VALUES (
#					%s, %s, %s, %s, %s, %s )""",(datetime.now(),storeid, bozo, label[:100], label[:200], labelmini[:50]))
#		
        # recherche des motifs des images/liens

	#Si on a bien eu une boucle for, on postprocess le magasin
	if newlatestimg is not None:
		cur.execute(
	"""INSERT INTO alilastscan (scandate, latestimg, idstore)
	    VALUES (%s,%s,%s)
	    ON CONFLICT (idstore) DO UPDATE SET scandate = EXCLUDED.scandate, latestimg = EXCLUDED.latestimg
	""", (datetime.now(), newlatestimg, storeid))
	
	# pour l'instant on ne gere qu'un store
	break

conn.commit()
cur.close()
conn.close()


exit()

#right minis get label
#	  <li class="item-sku-image"><a data-role="sku" data-sku-id="200003886" id="sku-1-200003886" title="941 Without Box" href="javascript:;"><img src="https://ae01.alicdn.com/kf/HTB1x3wpdYAaBuNjt_igq6z5ApXau/XH-948-Super-H-ros-Unique-Vente-Chiffres-Faucon-Assembler-Guerre-Machine-D-action-Vision-Briques.jpg_50x50.jpg" title="941 Without Box" bigpic="https://ae01.alicdn.com/kf/HTB1x3wpdYAaBuNjt_igq6z5ApXau/XH-948-Super-H-ros-Unique-Vente-Chiffres-Faucon-Assembler-Guerre-Machine-D-action-Vision-Briques.jpg_640x640.jpg"/></a></li>
                                                                                               
# left menu page itself
# 	<li><span class="img-thumb-item"><img alt="XH 948 Super H&eacute;ros Unique Vente Chiffres Faucon Assembler Guerre Machine D&#39;action Vision Briques Blocs de Construction Pour Enfants Jouets Cadeau" src="https://ae01.alicdn.com/kf/HTB1G0Z8XxTpK1RjSZFMq6zG_VXaP/XH-948-Super-H-ros-Unique-Vente-Chiffres-Faucon-Assembler-Guerre-Machine-D-action-Vision-Briques.jpg_50x50.jpg"/></span></li>
			
