import requests
import time
import math
    
class Word:
    def __init__(self, word):
        self.word = word
        self.score = 0
    
    def word(self):
        return self.word
    def score(self):
        return self.score
    
    
    
class Player:
    def __init__(self, current_game, game_id, player_key):
        self.game_id = game_id
        self.player_key = player_key
        
        self.language = current_game['language']
        file_url = f'{base_url}{self.language}'
        
        self.length = int(current_game['word_length'])
        self.number_of_words = int(current_game['words_count'])
        
        r = requests.get(file_url)
        requests.enconding = 'cp1252'
        text = r.content.decode('cp1252', errors='ignore')
        text_list = text.split('\n')
        
        
        #Lista en donde se guardan todas las palabras en el diccionario que cumplan con el largo.
        self.all_words = [w.strip().upper() for w in text_list if (len(w) == self.length )] 
        
        #Lista de palabras posibles para cada una de las palabras por adivinar.
        self.words_lists = [self.all_words for i in range(self.number_of_words )]
            
        #Lista de palabras posibles que se intenta adivinar actualmente
        self.current_words = self.all_words
        #Lista con palabras posibles & puntajes que se intenta adivinar actualmente
        self.scored_current_words = self.all_words
        #Número de palabra que se intenta adivinar actualmente
        self.current_list = -1
        
        self.rank = {}
        
        self.word = " "
        
        
        #Resultado para cada palabra en el último intento
        self.guessed = [ [] for i in range(self.number_of_words)]
        
        
        #Palabra que se intenta adivinar actualmente
        self.guessing_word = [0]*self.length
        
        #Verifica si la palabra ya ha sido adivinada.
        self.word_list_state = [False] * self.number_of_words
        

                
    def Alphabet(self):
        #Se guardan todos los carácteres posibles dentro de este 'diccionario' de palabras.
        self.alphabet = {}
        for word in self.current_words :
            for i in range(len(word)):
                letter = word[i]
                if letter not in self.alphabet.keys():
                    frequency = [0] * self.length
                    self.alphabet[letter] = frequency
                    self.alphabet[letter][i] += 1
                else:
                    self.alphabet[letter][i] += 1
    
    
    def Rank_Letters(self):
        #Se ordenan las palabras del alfabeto de la menos a la más popular, según su frecuencia en el diccionario.
        #Se podría hacer un ranking posicional supongo, pero no me dio el tiempo para esta entrega.
        self.rank = {}
        for letter in self.alphabet.keys():
            score = 0
            for x in self.alphabet[letter]:
                score += x
            self.rank[letter] = score
        self.rank = dict(sorted(self.rank.items(), key=lambda item: item[1]))
        
        i=1
        for letter in self.rank.keys():
            self.rank[letter] = i
            i += 1
    
    
    #Se define la palabra que se intentará adivinar en el próximo turno, eligiendo la palabra
    #que tenga menos opciones posibles (pues es más probable adivinar).
    def Set_Current_Words(self):
        min_len = 1000000000
        for i in range(self.number_of_words):
            word_list = self.words_lists[i]
            if len(word_list) < min_len and len(word_list) > 0 and self.word_list_state[i] == False :
                min_len = len(word_list)
                self.current_words = word_list
                self.current_list = i
            
                
    def Set_Scores(self, turno):
        #Se asignan los puntajes a cada palabra. Este se calcula sumando la frecuencia de cada letra según su posición.
        
        #Elegimos la palabra que queremos adivinar y
        #rearmamos el alfabeto para actualizar poder actualizar los puntajes.
        self.Set_Current_Words()
        self.Alphabet()
        self.scored_current_words = []
        for w in self.current_words:
            new_word = Word(w)
            mask = {}
            self.prob  = 1
            for i in range(len(w)):
                letter = w[i]

                #Solo sumo puntos por letras en posiciones no adivinadas
                if self.guessing_word[i] != 2:
                                        
                    #Solo sumo el valor de la letra una vez
                    if letter not in mask.keys():
                        new_word.score += self.alphabet[letter][i]
                        mask[letter] = self.alphabet[letter][i]
                        
                    #Si la letra está repetida, tomo el valor más alto de la letra
                    else:
                        max_letter_score = max(mask[letter], self.alphabet[letter][i])
                        new_word.score -= mask[letter] 
                        new_word.score += max_letter_score 
                        mask[letter] = max_letter_score
            
            
            #En la práctica se dió que haciendo esto mejoraba la precisión de los intentos. La idea detrás es que si no 
            #tengo ningún '2',me gustaría darle más prioridad, o un poco de ventaja,
            #a las letras que son menos probable de salir. Sirve, especialmente, para los casos en que tenemos
            #muchas palabras con una misma secuencia de caracteres a la respuesta.
            #lo que hago para evitar eso, es que aquí  tomo un mayor riesgo con la letra que escojo, puesto que tengo pocos
            #aciertos y un mayor riesgo puede ser más ventajoso.
            if self.guessing_word.count(2) <= 1:
                min_rank = 100000000
                flag = 0
                for letter in mask.keys():
                    for i in range(self.length):
                        if self.guessing_word[i] != 2:
                            flag = 1
                    if self.rank[letter] < min_rank and flag == 1 :
                        min_rank = self.rank[letter]
                new_word.score += min_rank
            
            self.scored_current_words.append(new_word)
        ###
        
        
    def Select_Word(self):
        #Se selecciona la mejor palabra según la que tenga el ptje más alto.
        max_score = 0
        chosen_word = ""
        for w in self.scored_current_words:
            if w.score > max_score:
                chosen_word = w.word
                max_score = w.score
        return chosen_word
       
        
    def Make_Guess(self, turno):
        #Aquí se envía la palabra elegida a la API y se procesa la respuesta. Si 'finished'= 'True'significa 
        #que ganamos el juego.
        
        #self.word es la palabra que uso para advinar. Entiendo que no es el nombre más descriptivo, pero ya es muy
        #tarde para cambiarlo 
        self.word = self.Select_Word()
            
        data = {
            'game': self.game_id,
            'key': self.player_key,
            'word': self.word
        }
        r = requests.post(f'{base_url}/api/play/', data=data)
        #print(r.json())
        finished = r.json()['finished']
        
        
        results = r.json()['result']     
        self.guessed = [ [] for i in range(self.number_of_words)]        
        
        
        #Se escriben los resultados recibidos de la API en el último intento.
        for word in range(self.number_of_words):    
            for letter in range(self.length):
                self.guessed[word].append(int(results[word][letter]))
          
        #Si se adivino alguna palabra, actualizamos la información en el programa.
        for i in range(len(r.json()['words_state'])):
            state = r.json()['words_state'][i]
            
            if state == True and self.word_list_state[i] != True :
                print("{}. {}".format(turno, self.word))
                self.word_list_state[i] = True

        return finished        
    
    
    
    def Review_Letters(self):
        #Aquí se analiza la respuesta recibida de la API sobre nuestro último intento y se va guardando 
        #las palabras que sigan cumpliendo las condiciones de posible respuesta.
        
        #Esto lo haremos para cada una de las palabras que queden por adivinar, por lo que se pierde bastante tiempo
        #en esta etapa.
        for list_number in range(self.number_of_words):
            
            #Para intentar ahorrar un poco de tiempo, sólo modificamos su diccionario si la palabra no ha sido adivinada.
            #No hace mucho efecto...
            if self.word_list_state[list_number] != True:
                possible_words = []
                for word in self.words_lists[list_number]:
                    word = word
                    possible_words.append(word)
                
                bad = []
                partial = []
                correct = []
                
                #Se agregan letras que sabemos son correctas
                for i in range(self.length):
                    if self.guessed[list_number][i] == 2:    
                        correct.append([self.word[i], i])
                        
                #Se agregan letras que son correctas pero en la posición equivocada
                for i in range(self.length):
                    if self.guessed[list_number][i] == 1:
                        partial.append([self.word[i], i])
                
                #Se agregan letras que no son correctas
                for i in range(self.length):
                    if self.guessed[list_number][i] == 0: 
                        bad.append(self.word[i])
                    
                #Letras que se encuentran en la palabra
                good_letters = []
                for correct_letter in correct:
                    good_letters.append(correct_letter[0])
                for partial_letter in partial:
                    good_letters.append(partial_letter[0])
                
                
                not_bad_words = []
                for word in possible_words:
                    flag = 0
                    for bad_letter in bad:
                        if bad_letter in word:    
                            #Si la letra está en good_letters y en bad es porque la letra sí esta en el resultado, solo que no está
                            #repetida más de una cierta cantidad de veces. Por lo tanto, sí agregamos la palabra que tenga esta letra.
                            if bad_letter in good_letters:
                                pass
                            
                            #La letra no está en la palabra <=> No la agregamos
                            else:
                                flag = 1
                                break
                    if flag == 0:
                        not_bad_words.append(word)
            
                
                not_correct_words = []
                for word in not_bad_words:
                    flag = 0
                    for correct_letter in correct:   
                        #Si la letra correcta no está en la posición correcta, entonces no agregamos la palabra.
                        if word[correct_letter[1]] != correct_letter[0]:
                            flag = 1
                            break     
                    if flag == 0:
                        not_correct_words.append(word)
                
                
                not_partial_words = []
                for word in not_correct_words:
                    flag = 0
                    for partial_letter in partial: 
                        #Si una letra parcialmente correcta está en la misma posición que ya probamos, entonces no agregamos la palabra.
                        if word[partial_letter[1]] == partial_letter[0]:
                            flag = 1
                            break
                    if flag == 0:
                        not_partial_words.append(word)
                
                
                not_good_words = []
                for word in not_partial_words:
                    flag = 0
                    for good_letter in good_letters:
                        #La palabra no tiene la letra que sabemos que pertenece
                        if good_letter not in word:
                            flag = 1
                            break
                    if flag == 0:
                        not_good_words.append(word)
                        
                
                good_words = []
                for word in not_good_words:
                    flag = 0
                    for bad_letter in bad:
                        if bad_letter in good_letters:       
                            #Si de las palabras restantes (que no descartamos) tenemos una letra que es mala y buena al mismo tiempo,
                            #querríamos comprobar que la palabra tiene la letra exactamente la misma cantidad de veces que
                            #la palabra correcta.
                            if word.count(bad_letter) != good_letters.count(bad_letter):
                                flag = 1
                                break
                    if flag == 0:
                        good_words.append(word)
                self.words_lists[list_number] = good_words

    
    
def Set_Words(self, turno):
    #Preparamos las palabras para el siguiete turno. Es decir, recalculamos los puntajes posicinoales de cada letra
    #y se los asignamos denuevo a cada palabra.
    self.Review_Letters()
    self.Set_Scores(turno)        
    

def play(game_, player_key):
    response = requests.get(f'{base_url}/api/games/')
    games = response.json()['games']
        
    for g in games:
        if int(g['id']) == game:
            current_game = g
            break
    
    player = Player(current_game, game, player_key)
    
    turno = 1
    player.Alphabet()
    player.Rank_Letters()
    player.Set_Scores(turno)
    
    
    finished = False
    while not finished:  
        #if player.check()
        finished = player.Make_Guess(turno)
        if finished:
            break
        
        turno += 1
        player.Set_Words(turno)
    
    
    return turno


def reset(game, player_key):
    data = {
    'game': game,
    'key': player_key
    }
    r = requests.post(f'{base_url}/api/reset/', data=data)
    print(r.json())


base_url = 'https://pds-wordie.herokuapp.com'
player_key = 'XBRKGBA'

valor = 0


ids = [6, 7, 25, 26, 27, 28, 29, 30,
31, 32, 33, 34, 35, 36, 37, 38, 39, 40,
41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
51, 52, 53, 54]


#ids = [6]

for i in ids:
    game = i
    reset(game, player_key)
    
start = time.time()
for i in ids:
    game = i
    print("\nGame {}. Suma de turnos actual: {}".format(i, valor))
    valor += play(game, player_key)

print("Me tardé {} turnos en resolver los {} juegos. Fin.".format(valor, len(ids)))

end = time.time()
total_time_seconds = end - start

total_time_minutes, total_time_seconds = divmod(total_time_seconds, 60)
print("Me tardé {} minutos y {} segundo".format(int(total_time_minutes), int(total_time_seconds) + 1))

