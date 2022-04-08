import copy
from automata.fa.dfa import DFA
from visual_automata.fa.dfa import VisualDFA
from automata.fa.nfa import NFA
from visual_automata.fa.nfa import VisualNFA
import json

file = open('input2.json')
input_nfa = json.load(file)

#citire date initiale din fisier
if type(input_nfa['states']) is list:
    stari = set(input_nfa['states'])
else:
    stari = set()
    stari.add(input_nfa['states'])

if type(input_nfa['input_symbols']) is list:
    alfabet = set(input_nfa['input_symbols'])
else:
    alfabet = set()
    alfabet.add(input_nfa['input_symbols'])

tranzitii = input_nfa['transitions']


for key1 in tranzitii:
    for key2 in tranzitii[key1]:
        if type(tranzitii[key1][key2]) is list:
            tranzitii[key1][key2] = set(tranzitii[key1][key2])

stare_initiala = input_nfa['initial_state']

if type(input_nfa['final_states']) is list:
    stari_finale = set(input_nfa['final_states'])
else:
    stari_finale = set()
    stari_finale.add(input_nfa['final_states'])


#declaram NFA pentru a reprezenta grafic
nfa=NFA(states=stari, input_symbols=alfabet, transitions=tranzitii, initial_state=stare_initiala, final_states=stari_finale)
nfa1 = VisualNFA(nfa)
nfa1.show_diagram(filename="NFA_cu_Lambda",view=True)


#lista cu stari si alfabet
stari1=list(stari)
alfabet1=list(alfabet)



def EClosure(state):
    closure = dict()
    closure[state] = 0
    Dstates = [state]
    while (len(Dstates) > 0):
        cur = Dstates.pop(0)
        if '' in tranzitii[cur]:
            for x in tranzitii[cur][""]:
                if x not in closure.keys():
                    closure[x] = 0
                    Dstates.append(x)
        closure[cur] = 1
    return closure.keys()


epsilon_closure = dict()
for x in stari1:
    epsilon_closure[x] = list(EClosure(x))

dfa_stack = list()#stiva
dfa_stack.append(epsilon_closure[stare_initiala])

#verific daca am in primul nod din AFD elementul stare_finala din NFA, daca il are atunci este stare finala si pt DFA si il memorez
for value in stari_finale:
    if value in dfa_stack[0]:
        dfa_stare_finala = set(dfa_stack[0])
        break

# List to store the states of AFD
dfa_states = list()
dfa_states.append(epsilon_closure[stare_initiala])
# Loop will run till this stack is not empty
translate_dfa=dict()
cnt=0
dfa_tranzitii=dict()
dfa_stare_finala=set()
while (len(dfa_stack) > 0):#epsilon clouser pt mai multe stari
    cnt += 1#ca sa imi pot da numele (s1, s2, s3, ...)
    cur_state = dfa_stack.pop(0)
    translate_dfa[cnt] = set(cur_state)#ca sa imi traduc din lista in id starii {s1:{p,q,t},s2:{},...}
    cv = dict()
    for al in alfabet1:
        from_closure = list()#retinem pentur fiecare element din alfabet unde duce din starea curenta
        for x in cur_state:
            if al in tranzitii[x]:
                cv[al] = set()
                cv[al].update(tranzitii[x][al])
                from_closure.append(set(tranzitii[x][al]))#retinem pentur fiecare element din alfabet unde duce din starea curenta
        if (len(from_closure) > 0):# verificam daca am gasit stari in care ne ducem cu alfabetul
            to_state = set()#starea in care se merge cu elementul din alfabet al
            uha="s"+str(cnt)#id stare
            dfa_tranzitii[uha] = cv#imi adaug in dictionar tranzitiile gasite mai sus
            # print(from_closure)
            # print()
            for x in list(from_closure):
                for j in x:
                    to_state.update(set(epsilon_closure[j])) #adaugam toate starile AFN in care se merge prin litera al din alfabet
            if list(to_state) not in dfa_states:
                dfa_stack.append(list(to_state))
                dfa_states.append(list(to_state))
                if stari_finale in list(to_state):#verific sa apara satrile finale din AFN, daca apar atunci DFA devine stare finala
                    dfa_stare_finala.add(set(to_state))
        else:
            if (list("d")) not in dfa_states:
                dfa_states.append(list("d"))

#adaug starea de vid (null) (s5 in cazu exemplului ales)
ok="s"+str(len(translate_dfa.items())+1)
cv1 = dict()
dfa_tranzitii[ok] = cv1# Adaug in tranzitie si drumurile pt dead


cnt2=0
dfa_stari=set() #imi construiesc un set cu toate starile pt AFD (s1, s2, s3, ...) in loc sa fie sub forma {p,t,q}, {}
for _ in dfa_states:
    cnt2+=1
    dfa_stari.add("s%d"%cnt2)



#imi caut starea initiala in AFD
for nume,val in translate_dfa.items():
    ok3=1
    for clo in epsilon_closure[stare_initiala]:
        if clo not in val:
            ok3=0
    if ok3==1:
        ok = "s" + str(nume)
        dfa_stare_initiala = ok


for i in dfa_states:#imi caut starea finala in AFD
    for sf in stari_finale:
        if sf in i:
            for nume, val in translate_dfa.items():#caut sa gasesc id-ul stari
                if set(i) == val:  # caut ce id ar trebuii sa aiba starea finala
                    ok = "s" + str(nume)
                    dfa_stare_finala.add(ok)

#ordonez crescator translate_dfa ca sa mearga spercamerge=dfa_tranzitii[key1][key2].intersection(translate_dfa[idx])
def sort_by_values_len(dictio):
    dict_len= {key: len(value) for key, value in dictio.items()}#dictinar cu {element:lungime, ...} ex. {1:3, 2:2, ...}
    import operator
    sorted_key_list = sorted(dict_len.items(), key=operator.itemgetter(1))
    sorted_dict=dict()
    for item in sorted_key_list:
        sorted_dict[item[0]]=dictio[item[0]]
    return sorted_dict

#ordonez crescator translate_dfa ca sa mearga spercamerge=dfa_tranzitii[key1][key2].intersection(translate_dfa[idx])
translate_dfa1=sort_by_values_len(translate_dfa)
# translate_dfa1=translate_dfa
dfa_tranzitii1=dict()
print(translate_dfa)
print(dfa_tranzitii)
#imi reconstruiesc un dictionar cu tranzitii pt dfa in care sa am id-ul potrivit nu elementele din AFN
for key1 in dfa_tranzitii.keys():
    var=dict()
    for key2 in alfabet1:
        for idx in translate_dfa1.keys():
            if key2 in dfa_tranzitii[key1]:
                print(dfa_tranzitii[key1][key2], "          ", translate_dfa1[idx])
                spercamerge=dfa_tranzitii[key1][key2].intersection(translate_dfa1[idx])#daca da "set()"inaseamna ca nu s-a gasit nimic pt intersectie si returneaza un set gol
                print("=>")
                print(spercamerge)
                # print()
                if spercamerge==dfa_tranzitii[key1][key2] :
                    print(idx)
                    var[key2]="s"+str(idx)
                    break
            else:
                var[key2] = "s5"
    dfa_tranzitii1[key1] = var
print(dfa_tranzitii1)
print(dfa_stari)
#declar un AFD cu datele calculate pentru a reprezenta grafic AFD-ul
dfa=DFA(states=dfa_stari,input_symbols=alfabet,transitions=dfa_tranzitii1,initial_state=dfa_stare_initiala,final_states=dfa_stare_finala)

#reprezentarea grafica a AFD-ului
dfa = VisualDFA(dfa)
# dfa.show_diagram(filename="DFA",view=True)
