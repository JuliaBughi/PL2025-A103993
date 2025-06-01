tests = []

#0
tests.append("""
prOgRam Example;
var
    x, y: integer;
    z: real;
    s: string;
begin
    x := 10;
    y := 20;
    z := 3.14;
    s := 'Hello,    world!';

    if (x < y) and (z > 3.0) then
        writeln('x is less than y and z is greater than 3.0')
    else
        writeln('Condition not met');

    (* Este é um comentário 
    de múltiplas linhas *)
    { Este é outro tipo de comentário }

    for x := 1 to 10 do
        writeln(x)
end.
""")

#1
tests.append("""
program HelloWorld;
begin
    writeln('Ola, Mundo!');
end.
""")

#2
tests.append("""
program Maior3;
var
    num1, num2, num3, maior: Integer;
begin
    { Ler 3 números }
    Write('Introduza o primeiro número: ');
    ReadLn(num1);
    Write('Introduza o segundo número: ');
    ReadLn(num2);
    Write('Introduza o terceiro número: ');
    ReadLn(num3);
    { Calcular o maior }
    if num1 > num2 then
        if num1 > num3 then maior := num1
        else maior := num3
    else
        if num2 > num3 then maior := num2
        else maior := num3;
    { Escrever o resultado }
    WriteLn('O maior é: ', maior)
end.
""")

#3
tests.append("""
    program Fatorial;
    var
        n, i, fat: integer;
    begin
        writeln('Introduza um número inteiro positivo:');
        readln(n);
        fat := 1;
        for i := 1 to n do
            fat := fat * i;
        writeln('Fatorial de ', n, ': ', fat);
    end.
""")

#4
tests.append("""
    program NumeroPrimo;
    var
        num, i: integer;
        primo: boolean;
    begin
        writeln('Introduza um número inteiro positivo:');
        readln(num);
        primo := true;
        i := 2;
        while (i <= (num div 2)) and primo do
            begin
                if (num mod i) = 0 then
                    primo := false;
                i := i + 1;
            end;
        if primo then
            writeln(num, ' é um número primo')
        else
            writeln(num, ' não é um número primo')
    end.
""")

#5
tests.append("""
    program SomaArray;
    var
        numeros: array[1..5] of integer;
        i, soma: integer;
    begin
        soma := 0;
        writeln('Introduza 5 números inteiros:');
        for i := 1 to 5 do
        begin
            readln(numeros[i]);
            soma := soma + numeros[i];
        end;
    
        writeln('A soma dos números é: ', soma);
    end.
""")

#6
tests.append("""
    program BinarioParaInteiro;
    var
        bin: string;
        i, valor, potencia: integer;
    begin
        writeln('Introduza uma string binária:');
        readln(bin);
             
        valor := 0;
        potencia := 1;
        for i := length(bin) downto 1 do
        begin
            if bin[i] = '1' then
                valor := valor + potencia;
            potencia := potencia * 2;
        end;
             
        writeln('O valor inteiro correspondente é: ', valor);
    end.
""")

#7
tests.append("""
    program BinarioParaInteiro;
             
    function BinToInt(bin: string): integer;
    var
        i, valor, potencia: integer;
    begin
        valor := 0;
        potencia := 1;
             
    for i := length(bin) downto 1 do
    begin
        if bin[i] = '1' then
            valor := valor + potencia;
        potencia := potencia * 2;
    end;
             
        BinToInt := valor;
    end;
             
    var
        bin: string;
        valor: integer;
    begin
        writeln('Introduza uma string binária:');
        readln(bin);
        valor := BinToInt(bin);
        writeln('O valor inteiro correspondente é: ', valor);
    end.
""")

#8
tests.append("""
program TestRepeatCase;
var
    i: integer;
    option: integer;
begin
    i := 0;
    repeat
        writeln('Counter: ', i);
        i := i + 1;
    until i > 5;

    option := 2;
    case option of
        1: writeln('Option is one');
        2: writeln('Option is two');
        3, 4: writeln('Option is three or four');
    end
end.
""")

#Testes semanticos errados

#9 -> somar integer com string
tests.append("""program Falha1;
var
    resultado: integer;
begin
    resultado := 5 + 'mundo';
    writeln(resultado);
end.
""")

#10 -> atribuir string a integer
tests.append("""program Falha2;
var
    numero: integer;
begin
    numero := 'hello';
    writeln(numero);
end.
""")

#11 -> comparar integer com string
tests.append("""program Falha3;
var
    x: integer;
begin
    x := 10;
    if x > 'abc' then
        writeln('Impossível');
end.
""")

#12 -> usar string como boolean
tests.append("""program Falha3;
var
    x: integer;
begin
    x := 10;
    if 'abc' then
        writeln('Impossível');
end.
""")

#13 -> usar variável integer como boolean
tests.append("""program Falha6;
var
    x: integer;
begin
    x := 5;
    if x then
        writeln('Erro: integer usado como boolean');
end.
""")

#14 -> modificação constante
tests.append("""program Falha9;
const
    PI = 3.14159;
var
    x: real;
begin
    PI := 2.71;
    writeln(PI);
end.""")

#15 -> variável não usada
tests.append("""program Falha11;
var
    n: integer;
    x: integer;
begin
    x := 10 + 1;
    writeln(x);
end.""")

#16 -> função não usada
tests.append("""program Falha12;

function FuncaoInutilizada(x: integer): integer;
begin
    FuncaoInutilizada := x * 2;
end;

var
    resultado: integer;
begin
    resultado := 5;
    writeln(resultado);
end.""")

#17 -> função com parâmetro não usado
tests.append("""program Falha13;

function Calculo(usado: integer, n: string): integer;
begin
    Calculo := usado + 10;
end;

var
    resultado: integer;
begin
    resultado := Calculo(5, 'teste');
    writeln(resultado);
end.""")