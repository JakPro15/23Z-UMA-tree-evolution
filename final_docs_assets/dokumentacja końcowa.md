---
geometry: "left=2cm,right=2cm,top=2cm,bottom=2cm"
---

# UMA Projekt – Ewolucja drzewa
## Dokumentacja końcowa
Skład zespołu:\
Jakub Proboszcz 318713\
Paweł Kochański 318673

### 1. Temat projektu
„Ewolucja drzewa\
Tworzenie drzewa decyzyjnego przy pomocy algorytmu ewolucyjnego. Zwykle klasyfikatory budowane są w oparciu o metodę zachłanną - w kolejnym kroku wybieramy lokalnie najlepszy podział. Takie podejście jest bardzo szybkie jednak nie zawsze prowadzi do utworzenia optymalnej struktury drzewa.”

### 2. Ustalenia z dokumentacji wstępnej i konsultacji

#### Doprecyzowanie tematu\
Zaimplementowanie algorytmu tworzącego na podstawie danych wejściowych drzewo decyzyjne z użyciem metod typowych dla algorytmu ewolucyjnego. Algorytm ewolucyjny umożliwia eksplorację różnych konfiguracji, dążąc do znalezienia bardziej globalnie optymalnego drzewa decyzyjnego, w odróżnieniu od zachłannych metod stosowanych w zwykłych klasyfikatorach. Zbadanie efektywności powstałych drzew i porównanie ich z istniejącą implementacją algorytmu ID3.


#### Wybrany wariant drzewa decyzyjnego\
W używanym przez nas wariancie drzewa decyzyjnego każdemu węzłowi niebędącemu liściem przypisany jest **atrybut** $a(x)$ i **wartość graniczna** $A$. Każdy taki węzeł ma 2 dzieci - lewe jest wybierane, jeżeli (dla obecnie rozważanego przykładu $\bar{x}$) spełniony jest warunek $a(\bar{x})<A$, a prawe w przeciwnym przypadku ($a(\bar{x})\ge A$).

Każdemu liściowi przyporządkowana jest **klasa**, przydzielana przykładom które do tego liścia trafią.

Z takich drzew składa się populacja w zaimplementowanym przez nas algorytmie ewolucyjnym.


#### Inicjalizacja populacji\
Każdy węzeł każdego drzewa w populacji startowej jest generowany następująco:\
Jeżeli osiągnięto maksymalną głębokość drzewa lub z prawdopodobieństwem ```leaf_probability(depth)``` węzeł będzie liściem.\
Jeżeli węzeł jest liściem, przypisywana jest mu klasa odpowiadająca klasie większościowej (najliczniejsza) z części zbioru danych, która trafia do tego liścia.\
Jeżeli w tym podzbiorze jest kilka równolicznych najliczniejszych klas, wybierana jest losowa z nich.\
Jeżeli do tego liścia nie trafia ani jeden przykład ze zbioru danych, klasa jest losowana.\
Jeżeli węzeł nie jest liściem, losowany jest atrybut, według którego następuje podział. Następnie, granica podziału jest losowana z dziedziny tego atrybutu. Dzieci tego węzła są generowane rekurencyjnie; zbiór danych otrzymany przez ten węzeł jest dzielony według wylosowanego atrybutu i granicy podziału i podzbiory są przekazywane dzieciom.\
Jeżeli zdarzy się sytuacja, że oboje dzieci danego węzła to liście z tą samą klasą, klasa prawego dziecka jest zmieniana na inną, losową.

W dokumentacji wstępnej klasa liścia miała być losowa, a nie większościowa - zostało to zmienione zgodnie z uwagą z maila.


#### Reprodukcja\
Wykonaliśmy eksperymenty z użyciem 4 wariantów reprodukcji: proporcjonalnej, rangowej, progowej i turniejowej. W naszym algorytmie ewolucji drzewa działają one tak samo, jak w zwykłym algorytmie ewolucyjnym.


#### Mutacja\
Mutacja polega na wylosowaniu jednego spośród węzłów drzewa. Z prawdopodobieństwem ```leaf_inner_swap_probability``` jest on zamieniany z liścia na węzeł wewnętrzny lub odwrotnie.\
Przy zmianie z liścia na węzeł wewnętrzny, atrybut, granica podziału i dzieci są generowane tak, jak w przypadku inicjalizacji, z tym, że dzieci zawsze będą liśćmi.\
Przy zmianie z węzła wewnętrznego na liść, klasa nowego liścia jest ustalana na losową spośród najliczniejszych klas wśród liści poddrzewa, którego korzeniem jest mutowany węzeł. Poddrzewo to jest odrzucane.\
Jeżeli nie zachodzi taka zamiana i węzeł jest liściem, to jego klasa jest zmieniana na losową inną. Jeżeli jest ona taka sama, jak klasa drugiego liścia z tym samym rodzicem, to rodzic jest zamieniany w liść z klasą taką, jaką miały jego dzieci.\
Jeżeli nie zachodzi taka zamiana i węzeł jest węzłem wewnętrznym, to jego atrybut jest zmieniany na losowy, a granica podziału jest ponownie losowana z dziedziny nowo wylosowanego atrybutu.

W dokumentacji wstępnej nie było zamiany węzła wewnętrznego w liść - zostało to zmienione zgodnie z uwagą z maila.


#### Krzyżowanie\
Krzyżowanie polega na wyborze dwóch węzłów w obu krzyżowanych drzewach oraz zamianie ich miejscami, razem z ich poddrzewami.\
Jeżeli jedno z drzew potomnych ma głębokość większą niż parametr ```max_depth```, to zamiast niego jest zwracany jeden z rodziców.\
Jeżeli w drzewie potomnym wystąpi sytuacja, gdzie dwa liście ze wspólnym rodzicem mają taką samą klasę, to rodzic jest zastępowany przez liść z klasą, którą miały jego dzieci (analogicznie jak w mutacji).


#### Sukcesja\
Wykonywaliśmy eksperymenty z użyciem 2 wariantów sukcesji: generacyjnej i elitarnej. W naszym algorytmie ewolucji drzewa działają one tak samo, jak w zwykłym algorytmie ewolucyjnym.


#### Funkcja oceny\
Funkcją oceny używaną przez nas jest dokładność (*accuracy*), czyli iloraz liczby przykładów ze zbioru treningowego, któremu dane drzewo przydzieliło właściwą klasę oraz liczby wszystkich przykładów w zbiorze treningowym. Funkcja ta jest **maksymalizowana**.


#### Wybrane zbiory danych\
Wybraliśmy pięć zbiorów danych:

               nazwa zbioru danych  liczba atrybutów   liczba klas   liczba przykładów
---------------------------------- ------------------ ------------- -------------------
       glass_identification               9              6             214
         dry_bean_dataset                 16             7            13611
breast_cancer_wisconsin_diagnostic        30             2             569
               wine                       13             3             178
    high_diamond_ranked_10min             38             2            9879


Hiperłącza do nich oraz liczności ich klas są wymienione poniżej.

Zbiór danych glass_identification [[link]](http://archive.ics.uci.edu/dataset/42/glass+identification):

Przewidywanie rodzaju szkła na podstawie jego własności fizykochemicznych.

 nazwa klasy liczba wystąpień
------------ ----------------
     1             70
     2             76
     3             17
     5             13
     6             9
     7             29

Zbiór danych dry_bean_dataset [[link]](http://archive.ics.uci.edu/dataset/602/dry+bean+dataset):

Przewidywanie gatunku suszonej fasoli na podstawie cech zdjęcia pojedynczej fasolki.

 nazwa klasy liczba wystąpień
------------ ----------------
 BARBUNYA         1322
  BOMBAY          522
   CALI           1630
 DERMASON         3546
   HOROZ          1928
   SEKER          2027
   SIRA           2636

   Zbiór danych breast_cancer_wisconsin_diagnostic [[link]](http://archive.ics.uci.edu/dataset/17/breast+cancer+wisconsin+diagnostic):

Diagnoza rodzaju raka piersi na podstawie właściwości komórek pobranych z piersi.

 nazwa klasy liczba wystąpień
------------ ----------------
     B            357
     M            212

Zbiór danych wine [[link]](http://archive.ics.uci.edu/dataset/109/wine):

Przewidywanie rodzaju wina na podstawie jego cech fizykochemicznych.

 nazwa klasy liczba wystąpień
------------ ----------------
     1             59
     2             71
     3             48

Zbiór danych high_diamond_ranked_10min [[link]](https://www.kaggle.com/datasets/bobbyscience/league-of-legends-diamond-ranked-games-10-min):

Przyporządkowanie wyników (zwycięstwo/porażka) meczy rankingowych w grze „League of Legends" na podstawie statystyk meczu pobranych w jego dziesiątej minucie trwania.

 nazwa klasy liczba wystąpień
------------ ----------------
     0            4949
     1            4930


#### Metoda referencyjna\
Wyniki uzyskane przez nasz algorytm porównujemy z wynikami istniejącej implementacji algorytmu ID3:\
[ID3 - hiperłącze](https://pypi.org/project/decision-tree-id3/)


### 3. Poprawność implementacji

W celu weryfikacji poprawności implementacji algorytmu, przygotowaliśmy testy jednostkowe do jego części składowych niezawierających losowości. Są one zawarte w plikach test_tree.py oraz test_genetic_operations.py. Ponadto, sprawdziliśmy poprawność inicjalizacji drzewa oraz reprodukcji w pliku manual_testing.ipynb - dla inicjalizacji wypisujemy wygenerowane drzewo, a dla reprodukcji rysujemy histogram przybliżający, jak zostają wybrane osobniki w reprodukcji.

Poprawność całości implementacji algorytmu pokazuje też porównanie z wynikami algorytmu ID3, zawarte w poniższej sekcji.


### 4. Eksperymenty