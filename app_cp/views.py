import random
from urllib import request
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

CHAVE_ALFABETO_BASE62 = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'+'@#$&()[]'
CHAVE_POSSIBILIDADE_PRIMOS = [3511, 7901, 4513, 6581, 6229, 1129, 2339, 1009, 5827]
CHAVE_XOR = 0xF2D431B6A7C9E0D5F8B7E1C2A0F16D4F9B8E7A0C5D2F1A3B6C9E0D2A5F4B6C7

def home(request):
    return render(request, 'app_cp/home.html')

#Explicação:
#AJAX (fetch): O texto é enviado para a view encrypt_view usando uma requisição POST. O resultado é um JSON com o texto criptografado.
#CSRF Token: Incluí o token CSRF para segurança.
#JsonResponse: A view retorna o texto criptografado como JSON, que é exibido na página sem recarregar.
@csrf_exempt
def view_criptografar(request):
    if request.method == 'POST':
        texto = json.loads(request.body)
        
        textodigitado = texto.get('text', '')

        # Lógica de criptografia
        texto_encriptado = criptografar(textodigitado)

        return JsonResponse({'texto_encriptado': texto_encriptado})

@csrf_exempt
def view_descriptografar(request):
    if request.method == 'POST':
        texto_criptografado = json.loads(request.body)
        
        textodigitadocriptografado = texto_criptografado.get('text', '')

        # Lógica de descriptografia
        texto_descriptografado = descriptografar(textodigitadocriptografado.strip())

        return JsonResponse({'texto_descriptografado':texto_descriptografado})

def criptografar(texto):
    return multiplicar_ascii(texto_para_ascii(texto.strip()))

def descriptografar(texto):
    texto = texto.replace('%', ' ') # Substituir % por espaço
    texto_atual='' #Representa cada caractere do texto original
    possibilidades = CHAVE_POSSIBILIDADE_PRIMOS #Lista de números primos
    resultado='' #Resultado final
    for i in texto: #Percorrer caracteres do texto criptografado
        if i == ' ' or i == '\n': #Descriptografa letra por letra do texto criptografado
            #Desconverter da base62 e depois fazer a comparação do XOR com a chave do XOR
            texto_sem_base62_e_sem_xor = str(funcao_xor(desconverter_base62(texto_atual), CHAVE_XOR))
            #Captura o índice do número primo da lista de primos (primeiro caractere do texto sem base62 e sem XOR)
            posicao = int(texto_sem_base62_e_sem_xor[0])-1
            #Captura o resto do texto sem o índice
            ascii_multiplicado = int(texto_sem_base62_e_sem_xor[1:])
            #Captura o número primo que foi utilizado na multiplicação com o caractere em ASCII
            primo = possibilidades[posicao]
            #Transformar o número ASCII em caractere normal
            resultado += chr(ascii_multiplicado//primo)
            texto_atual = '' #Limpar o texto atual para o mesmo receber a próxima letra que está criptografada
        else:
            texto_atual+=i #Acidiona o caractere no texto atual, desde que não seja espaço ou o final do texto

    #texto = desconverter_base62(texto)

    #DEBUG:
    print(f'================== \n{resultado}\n==================')
    return resultado


def texto_para_ascii(texto): # transforma o texto original em ascii
    ascii = ''
    for caractere in texto:
        # Converte cada caractere para seu valor ASCII usando a função ord()
        valor_ascii = ord(caractere)
        # Adiciona o valor ASCII à string, separando por um espaço (ou outro delimitador)
        ascii += str(valor_ascii) + ' '
    # Remove o último espaço extra
    ascii = ascii.strip()
    return ascii

# multiplica cada número do ASCII por um primo aleatório de uma lista
def multiplicar_ascii(ascii): 
    # CHAVE: lista de números primos para serem escolhidos aleatoriamente
    possibilidades = CHAVE_POSSIBILIDADE_PRIMOS
    # CHAVE:Hexadecimal de 256 bits para ser utilizado no XOR
    chave_xor = CHAVE_XOR
    
    ascii_atual = ''
    ascii_multiplicado_resultado_xor_base62 = ''
    # Adicionar um número aleatório de 5 dígitos e o índice da lista no início do resultado ascii mutiplicado
    # rodar a string do ascii original e multimplicar número a número pelo primo escolhido
    for x in ascii+'#':
        if x == ' ' or x == '#' or x == '\n':
            escolha_aleatoria = random.choice(possibilidades) # escolhe um número da lista de primos aleatório
            # captura a posição do numero aleatorio na lista + 1 (não pode ser zero, pois se for zero não terá como desfazer o XOR com o mesmo resultado)
            posicao_escolha_aleatoria = possibilidades.index(escolha_aleatoria) + 1 
            #Colocar o número da posição concatenado com o ASCII atual, que está multiplicado pela escolha aleatória:
            ascii_multiplicado_resultado = str(posicao_escolha_aleatoria) + str((int(ascii_atual) * escolha_aleatoria)) + ' '
            #Aplicar o XOR comparando ASCII atual, que está multiplicado pela escolha aleatória, com a chave de 256 bits
            #transformar em String e adicionar um espaço no final:
            xor = funcao_xor(int(ascii_multiplicado_resultado.strip()), chave_xor)
            ascii_multiplicado_resultado_xor_base62 += str(converter_para_base62(xor)) + '%'
            # DEBUG:
            print('================================\n'
                + f'\nNúmero primo escolhido: {escolha_aleatoria}'
                + f'\nPosição do número primo escolhido: {posicao_escolha_aleatoria}'
                + f'\nPrimo X ASCII da letra atual: {ascii_multiplicado_resultado}'
                + f'\nXOR aplicado no resultado: {xor}'
                + f'\nXOR aplicado no resultado: {converter_para_base62(xor)}'
            )
            ascii_atual = ''
        else:
            ascii_atual += x
    # DEBUG:
    print('================================\n'
          + f'\nString em formato ASCII: {ascii}'
          )
    return ascii_multiplicado_resultado_xor_base62


def funcao_xor(texto, chave):
    return texto ^ chave

def converter_para_base62(numero):
    # Alfabeto da base 62 (dígitos + letras minúsculas e maiúsculas)
    alfabeto_base62 = CHAVE_ALFABETO_BASE62
    base = len(alfabeto_base62)  # base62 tem 62 caracteres + 8 caracteres especiais
    # Lista para armazenar os caracteres da base62
    base62 = []
    #Converter o número para base62
    while numero > 0:
        #Divide o número pela quantidade de caracteres da base62
        numero, resto = divmod(numero, base)
        #Adiciona na lista final o caractere do alfabeto da base62 de indice correpondente ao resto da divisão 
        base62.append(alfabeto_base62[resto])
    #Inverte a lista que foi construída fo fim para o início
    return ''.join(reversed(base62))

def desconverter_base62(base62):
    alfabeto_base62 = CHAVE_ALFABETO_BASE62 #Alfabeto da base 62
    base = len(alfabeto_base62) # base62 tem 62 caracteres + 8 caracteres especiais
    numero = 0
    for i in base62:
        #Descobrir o idenx na lista do alfabeto base62 correspondente ao caractere atual da base62
        valor_index = alfabeto_base62.index(i)
        #Remontar os restos das divisões feitas anteriormente (numero*70 + index)
        numero = numero * base + valor_index

    return numero