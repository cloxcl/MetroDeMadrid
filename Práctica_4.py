#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  1 13:28:30 2021

@author: claudiagonzaleznieto
"""

class LineException(Exception):
    def __init__(self, mensaje):
        self.mensaje = mensaje

class Line(object):
    def __init__(self, estaciones, tiempos, estado, tramo):
        self.estaciones = estaciones
        self.tiempos = tiempos
        self.estado = estado
        self.tramo = tramo
      
    def __repr__(self):
        inicio = ''
        for estacion in self.estaciones:
                inicio+= f"{estacion} --> "
        return inicio[:-4]     
    
    def contains_station(self, e):
        if e in self.estaciones:
            return True
        else:
            raise LineException(f"La estación {e} no pertenece a la línea de metro {self}")
            
    def previous_e(self, e):
        if self.contains_station(e): 
            if e == self.estaciones[0]:
                    raise LineException(f"La estación {e} es cabecera de línea")
            else:
                    pos_e = self.estaciones.index(e)
                    return self.estaciones[pos_e - 1]
                    
    
    def next_e(self, e):
        if self.contains_station(e):
            if e == self.estaciones[-1]:
                raise LineException(f"La estación {e} es cabecera de línea")
            else:
                pos_e = self.estaciones.index(e)
                return self.estaciones[pos_e + 1]
            
    def cost_origin2destination(self, start, finish):
        if self.contains_station(start) and self.contains_station(finish):
            if start == finish:
                return 0
            else:
                pos_start = min(self.estaciones.index(start), self.estaciones.index(finish))
                pos_finish = max(self.estaciones.index(start), self.estaciones.index(finish))
                return sum([self.tiempos[i] for i in range(pos_start, pos_finish)])          
            
            
class MetroException(Exception):
    def __init__(self, mensaje):
        self.mensaje = mensaje
            
class Metro(object):
    def __init__(self, lineas = {}, transbordos = {}):
        #Con los diccionarios vacíos, inicializamos el Metro de Madrid.
        self.lineas = lineas #Diccionario line_name : line_object
        self.transbordos = transbordos #Diccionario estación : line_name
        
                
    def __repr__(self):
        result = ''
        for line_name, line_object in self.lineas.items():
            result +=  line_name  + repr(line_object) + '\n'
        for estacion, transbordos in self.transbordos.items():
            result +=  estacion + '\n' + repr(transbordos) + '\n'
        return result
    
    def add_lines(self, line_name, line):
        if line_name in self.lineas:
            raise MetroException(f"{line_name} ya se encuentra integrada en la red de Metro de Madrid")
        else:
            self.lineas[line_name] = line
            self.add_connections(line_name)
            
    def get_line(self, line_name):
        try:
            line_name = line_name + '\n'
            return self.lineas[line_name]
        except KeyError:
            raise MetroException(f"{line_name} no es una línea del Metro")
        
    def add_connections(self, line_name):
        if line_name in self.lineas:
            line_object = self.lineas[line_name]
            lista_estaciones = line_object.estaciones
            for estacion in lista_estaciones:
                if estacion in self.transbordos:
                    self.transbordos[estacion].append(line_name.strip())
                else:
                        self.transbordos[estacion] = [line_name.strip()]
                        
    def get_connections(self, e, line_name):
        if line_name in self.lineas:
            if e in self.lineas[line_name].estaciones:
                conexiones = []
                for correspondencias in self.transbordos[e]:
                    conexiones.append(correspondencias)
                conexiones.remove(line_name)
                return conexiones
            else:
                raise MetroException(f"La estación {e} no pertenece a la línea {line_name}")
        else:
         raise MetroException(f"La línea {line_name} no pertenece a la red de Metro")
        
          
    @staticmethod
    def load_metro(file_name):
        #Abrimos el fichero
        f = open(file_name, 'r').readlines()
        
        #Guardamos los nombres de las líneas
        line_name = f[::2]
        
        #Guardamos las líneas (estaciones)
        lineas = f[1::2]
        
        #Lista que almacenará todos los objetos tipo Line, 16 en total
        line_object_list = []
        
        for linea in lineas:
            tiempos = []
            nombres_estaciones = []
            estados_estacion = [] #Lista de estaciones fantasma (se puede atravesar, pero no hacer transbordos)
            tramo_estacion = [] #Lista de estaciones intransitables (no se pueden atravesar)
            for elemento in linea.split('->'):
                if elemento.isnumeric():
                    tiempos.append(int(elemento))
                else:
                    nombres_estaciones.append(elemento.strip())
            for estados in range(len(nombres_estaciones)):
                estados_estacion.append('Abierta')
            for estado in range(len(nombres_estaciones)):
                tramo_estacion.append('Transitable')
            
                    
            #Tenemos la lista de estaciones, tiempos y estado de estaciones y vías, luego creamos el objeto Line
            line_object = Line(nombres_estaciones, tiempos, estados_estacion, tramo_estacion)
            
            #Line_object_list es ya la lista completa de objetos tipo Line
            line_object_list.append(line_object)
            
        metro = Metro()
        for x in range(16):
            metro.add_lines(line_name[x], line_object_list[x])
        return metro
    
                    
    def cost_origin2destination_transfer(self, start, finish):  
        if start in self.transbordos and finish in self.transbordos:
            
                #Primero abordamos la situación en que dos estaciones comparten más de una línea
            
                lineas_en_comun = [] #Lista de objetos Line
            
                for lineas_start in self.transbordos[start]:
                    if lineas_start in self.transbordos[finish]:
                        lineas_en_comun.append(self.get_line(lineas_start))
            
                if len(lineas_en_comun) >= 1 and lineas_en_comun != []:   
                
                    tiempos = []
            
                    for lineascomunes in lineas_en_comun:
                        tiempos.append(lineascomunes.cost_origin2destination(start, finish))
                    return min(tiempos)
            
            #Ahora veamos qué sucede cuando start y finish no comparten línea
            
            
                elif lineas_en_comun == []:
                    estaciones_transbordos = []
                    tiempos_transbordos = []
                    for linea_start in self.transbordos[start]:
                        for linea_finish in self.transbordos[finish]:
                            estaciones_transbordos.append(list(set(self.lineas[linea_start + '\n'].estaciones).intersection(set(self.lineas[linea_finish + '\n'].estaciones))))
                    estaciones_transbordos_ok = [item for lista in estaciones_transbordos for item in lista]
                    print(estaciones_transbordos_ok)
                    for transbordo in estaciones_transbordos_ok:
                         rty = set(set(self.transbordos[start])).intersection(set(self.transbordos[transbordo]))
                         uio = set(set(self.transbordos[transbordo])).intersection(set(self.transbordos[finish]))
                         for qwe in rty:
                             for dfg in uio:
                                     tiempos_transbordos.append(self.get_line(qwe).cost_origin2destination(start, transbordo) + self.get_line(dfg).cost_origin2destination(transbordo, finish) + 300)
                    print(tiempos_transbordos)
                    return min(tiempos_transbordos)
                
    def close_station(self, line_name, e):
        if not line_name  + '\n'  in self.lineas:
             raise MetroException(f"{line_name} no pertenece a la red de Metro.")
        else:
            linea = self.get_line(line_name)
            if linea.contains_station(e):
                indice = linea.estaciones.index(e)
                linea.estado[indice] = 'Cerrada'
            else:
                raise LineException(f"La estación {e} no pertenece a {line_name}.")
                 
    def get_closed_stations(self, line_name):
        if line_name+ '\n' in self.lineas:
            linea = self.get_line(line_name)
            estaciones_cerradas = [linea.estaciones[x] for x in range(len(linea.estaciones)) if linea.estado[x] == 'Cerrada']
            return estaciones_cerradas
        else: 
            raise MetroException(f"La línea {line_name} no pertenece a la red de Metro.")
            
    def open_station(self, line_name, e):
        if e in self.get_closed_stations(line_name):
            linea = self.get_line(line_name)
            indice = linea.estaciones.index(e)
            linea.estado[indice] = 'Abierta'
        else:
            pass
        
    def close_section(self, line_name, start, finish):
        if not line_name  + '\n'  in self.lineas:
             raise MetroException(f"{line_name} no pertenece a la red de Metro.")
        else:
                linea = self.get_line(line_name)
                if linea.contains_station(start) and linea.contains_station(finish):
                    pos_start = min(linea.estaciones.index(start), linea.estaciones.index(finish))
                    pos_finish = max(linea.estaciones.index(start), linea.estaciones.index(finish))
                    for indices in range(pos_start, pos_finish+1):
                        linea.tramo[indices] = 'Intransitable'
                else:
                     raise LineException(f"La estación {start} o {finish} no pertenece(n) a {line_name}.")
        
    def get_closed_section(self, line_name):
        try:
            linea = self.get_line(line_name)
            seccion_cerrada = [linea.estaciones[x] for x in range(len(linea.estaciones)) if linea.tramo[x] == 'Intransitable']
            return seccion_cerrada
        except line_name as KeyError:
            raise KeyError(f"{line_name} no pertenece al Metro.")
            
    def open_section(self, line_name):
        if line_name + '\n' in self.lineas:
            linea = self.get_line(line_name)
            if self.get_closed_section(line_name) != []:
                seccion_cerrada = self.get_closed_section(line_name)
                pos_start = linea.estaciones.index(seccion_cerrada[0])
                pos_finish = linea.estaciones.index(seccion_cerrada[-1])
                for x in range(pos_start, pos_finish + 1):
                    linea.tramo[x] = 'Transitable'
        else:
            raise MetroException(f"{line_name} no es una línea perteneciente a la red.")
