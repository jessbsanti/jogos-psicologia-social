FAST CONSENSUS MÍNIMO — oTree 6.0.15

1. Copie a pasta fast_consensus_min para a pasta do seu projeto oTree.

2. Abra settings.py e inclua uma sessão como esta em SESSION_CONFIGS:

 dict(
     name='fast_consensus_min',
     display_name='Fast Consensus mínimo',
     app_sequence=['fast_consensus_min'],
     num_demo_participants=3,
 ),

3. No terminal, dentro da pasta do projeto, execute:

 otree devserver

4. Abra o endereço mostrado no terminal e clique em "Fast Consensus mínimo".

5. Para testar sozinho, abra 3 abas ou 3 janelas anônimas usando os links de participante.

DADOS REGISTRADOS AUTOMATICAMENTE
- player.choice: alternativa escolhida
- player.response_time: tempo desde o início comum da rodada até a resposta, em segundos
- player.consensus_reached: 1 quando os três participantes escolheram a mesma alternativa; 0 caso contrário
- group.consensus_reached: indica se houve consenso total
- group.consensus_choice: alternativa consensual; fica vazia quando não há consenso
- player.question_text: texto da pergunta
- round_number: número da rodada

CRONÔMETRO SINCRONIZADO
- Antes de cada pergunta existe uma tela de espera.
- A rodada começa somente quando todos os jogadores do grupo chegam a essa tela.
- O servidor define um único horário de início e um único horário final para o grupo.
- Todos recebem o mesmo prazo de 30 segundos.
- Se alguém abrir a pergunta alguns instantes depois, verá apenas o tempo que ainda resta.
- Ao chegar a zero, a página é enviada automaticamente.
- Se nenhuma alternativa tiver sido marcada, choice fica vazio e matched_majority = 0.

CRITÉRIO DE CONSENSO
Há consenso somente quando os 3 participantes respondem e escolhem exatamente a mesma alternativa. Se houver duas ou mais escolhas diferentes, ou se alguém não responder, não há consenso.
