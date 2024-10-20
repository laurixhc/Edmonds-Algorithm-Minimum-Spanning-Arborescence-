import networkx as nx


#función que lee el documento y llama a la fucnión arborescencia
def leer_documento(grafos_doc):
    G = nx.DiGraph()
    with open(grafos_doc,'rb') as f:
        i = 0
        for linea in f:
            if i == 0:
                lista = linea.strip().split()
                raiz = lista[1].decode()
                i=1
            else:
                lista = linea.strip().split()
                G.add_edge(lista[0].decode(), lista[1].decode(), weight = int(lista[2]))

    arborescencia(G,raiz)

#función que a partir de un grafo y una raíz devuelve la arborescencia de minimo peso
def arborescencia(G,raiz):
    #creamos el digrafo resultado
    G_copia = G.copy()
    R = nx.DiGraph()
    R = reduccion(G,raiz)
    if (R==None):
        return
    #aplicamos la contraccion en el caso de existir ciclos
    ciclos = []
    e=list()
    while  len(list(nx.simple_cycles(R)))>0:
        ciclos.append(tuple(list(nx.simple_cycles(R))[0]))
        G,e = contraccion(G, R,e)
        R = reduccion (G,raiz)
        if (R==None):
            return
        
    #expendimos el grafo reducido
    resultado = expandir (G_copia, R, ciclos, e)
    #calculamos el peso
    peso = 0
    lista = resultado.edges(data= 'weight')
    for i in lista:
        peso += i[2]
    resultado_final = resultado.edges
    
    print('La arborescencia buscada es:', resultado_final)
    print('El peso es:', peso)
    #para dibujarlo
    pos = nx.shell_layout(resultado)
    nx.draw(resultado,pos,with_labels=True)   
    edge_labels = nx.get_edge_attributes(resultado, 'weight')
    nx.draw_networkx_edge_labels(resultado, pos, edge_labels=edge_labels)
    
    return resultado_final, peso
    
#funcion que reduce el grafo
def reduccion(G,raiz):

    #creamos el grafo final que devolveremos (el reducido de G)
    R = nx.DiGraph()
    R.add_nodes_from(list(G.nodes()))
    
    #tomamos para cada nodo la arista de menor peso
    for node in list(G.nodes):
        if(node!=raiz):
            if not any(edge[1] == node for edge in G.edges(data='weight')):
                print('No existe arborescencia')
                return
            arista_minima = min((edge for edge in G.edges(data='weight') if edge[1] == node), key=lambda x: x[2])
            R.add_edge(arista_minima[0],arista_minima[1],weight=arista_minima[2])
    
    return R
    

#funcion que contraer un circuito
def contraccion(G, G_reducido,e):
    R = nx.DiGraph()
    #tomamos un ciclo
    m = list(nx.simple_cycles(G_reducido))
    ciclo = m[0]
    
    #recorremos las aristas de G
    for edge in G.edges(data = 'weight'):
        #en el caso de estar el primer nodo en el ciclo y el segundo no
        if (edge[0] in ciclo) and (edge[1] not in ciclo):
            
            #en el cso de estar en el grafo R la arista, tomr la de menor peso
            if(R.has_edge(tuple(ciclo), edge[1]) and R.get_edge_data(tuple(ciclo), edge[1])['weight']>edge[2]):
                R.add_edge(tuple(ciclo), edge[1], weight = edge[2])
                e.append([(tuple(ciclo)), edge[1], edge[0],edge[2]])
             
            #en el caso de no estra la arista en R, añadimos la arista
            elif not R.has_edge(tuple(ciclo), edge[1]):
                R.add_edge(tuple(ciclo), edge[1], weight = edge[2])
                e.append([(tuple(ciclo)), edge[1], edge[0],edge[2]])
         
        #en el caso de estar el nodo final en el ciclo y el pimero no
        elif (edge[1] in ciclo) and (edge[0] not in ciclo):
            
            #tomamos las aristas cuyo nodo final es edge[1]
            aristas_con_i = [(u, v) for u, v in G.edges() if v == edge[1] and u in ciclo]
            peso= edge[2]-G.get_edge_data(aristas_con_i[0][0], aristas_con_i[0][1])['weight']
            for i in range(len(aristas_con_i)):
                if peso>edge[2]-G.get_edge_data(aristas_con_i[i][0], aristas_con_i[i][1])['weight']:
                    peso = edge[2]-G.get_edge_data(aristas_con_i[i][0], aristas_con_i[i][1])['weight']
                
            if(R.has_edge(edge[0], tuple(ciclo)) and R.get_edge_data(edge[0], tuple(ciclo))['weight']>peso):
                R.add_edge(edge[0], tuple(ciclo), weight = peso)
                e.append([edge[0],(tuple(ciclo)), edge[1], peso])
                
            elif not R.has_edge(edge[0], tuple(ciclo)) :
                R.add_edge(edge[0], tuple(ciclo), weight = peso)
                e.append([edge[0],(tuple(ciclo)), edge[1], peso])
         
        #en el caso de ninguno de los dos nodos estar en el ciclo
        elif (edge[0] not in ciclo) and (edge[1] not in ciclo):
            
            if(R.has_edge(edge[0], edge[1]) and R.get_edge_data(edge[0], edge[1])['weight']>edge[2]):
                R.add_edge(edge[0], edge[1], weight = edge[2])
                
            elif not R.has_edge(edge[0], edge[1]):
                R.add_edge(edge[0], edge[1], weight = edge[2])
    
    return R, e


            
 #función para expandir el grafo reducido       
def expandir(G,G_reducido, ciclos, e):  
    R = nx.DiGraph()

    #recorremos las aristas del grafo reduccido para irlas expendiendo
    for edge in G_reducido.edges:
        
        #si el nodo inicial está en el conjunto de ciclos y el final no, ya tendríamos de anteriormente 
        #el ciclo expandido, entonces tomamos el nodo final de la última arista y la unimos con el nodo final dado
        if (edge[0] in ciclos) and edge[1] not in ciclos:
            aristas = list(R.edges)
            nodo = (aristas[len(aristas)-1][1])
            peso = G.get_edge_data(nodo, edge[1])['weight']
            R.add_edge(nodo, edge[1], weight = peso)
                
 
        #en el caso de que el segundo nodo esté en el conjunto de ciclos, tomamos de e la arista que 
        #une al nodo inicial con el ciclo, y expandimos el ciclo
        elif (edge[1] in ciclos) :
            ciclo = list(edge[1])
            nodo = [i for i in e if i[0]==edge[0] and i[1]==edge[1]]
            peso = nodo[0][3]
            arista = [nodo[0][0], nodo[0][2]]

            #si el primer nodo tmabién es un ciclo, tomamos la última arista de R(como en el caso anterior)
            if (edge[0] in ciclos):
                aristas = list(R.edges)
                arista[0] = (aristas[len(aristas)-1][1])
                
            
            for i in nodo:
                if i[3]<peso:
                    peso=i[3]
                    arista = [i[0], i[2]]
            
            peso = G.get_edge_data(arista[0], arista[1])['weight']
            R.add_edge(arista[0], arista[1], weight = peso)
            ciclo.remove(arista[1])
            while (len(ciclo)>0):
                
                c = ciclo[0]
                nodos = [(u, v, peso) for u, v, peso in G.edges(data='weight') if v==c and u in edge[1]]    
                peso = nodos[0][2]
                arista = [nodos[0][0], nodos[0][1]]
                for i in nodos:
                    if i[2]<peso:
                        peso=i[2]
                        arista = [i[0], i[1]]
                ciclo.remove(arista[1])
                R.add_edge(arista[0],arista[1], weight = peso)
            
        # en el caso de que ningunon de los nodos esté en el conjunto de ciclos, la añadimos a R
        elif (edge[1] not in ciclos) and edge[0] not in ciclos:
            R.add_edge(edge[0],edge[1], weight = edge[2])
            
        
    return R
            
#leemos el documento donde tenemos el grafo que queremos leer  
leer_documento('grafos.txt')   
 
    
#EJEMPLOS

# G = nx.DiGraph()

# #G.add_weighted_edges_from([(1, 3, 8), (1, 2, 7),(1,4,9), (1, 5, 6), (3,2, 1),(2,6,5),(3,4,2),(4,3,2),(4,2,3),(5,6,2),(6,5,4),(6,4,3)])

# #G.add_weighted_edges_from([(1, 3, 8), (1, 2, 7),(1,4,9), (1, 6, 6),(2,4,2),(3,2,1), (3,5,5), (4,2,2), (4,3,3),(5,4,3), (5,6,4), (6,5,2)])

# G.add_weighted_edges_from([(0,1,3),(0,3,5),(0,5,4),(0,7,3),(1,3,4),(2,1,1),(3,2,5),(3,4,3),(3,6,6),(4,2,2),(5,6,3),(6,3,8),(6,7,2),(7,5,3),(7,4,6)])

 
# arborescencia(G,0)
