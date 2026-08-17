# BrAInChain

Plataforma de pesquisa e automação de **IA para criptomoedas**.

## Visão

O BrAInChain está sendo construído como uma plataforma orientada à pesquisa para descobrir padrões associados a movimentos extremos de preço em criptomoedas. O sistema coletará dados históricos e quase em tempo real, transformará observações em características, treinará e validará modelos de Machine Learning e, futuramente, poderá suportar Paper Trading antes de qualquer execução com dinheiro real.

**Importante:** a V1 é exclusivamente para pesquisa. Ela não realiza operações com dinheiro real.

## Escopo atual

- Arquitetura e documentação do projeto
- Interfaces de aquisição de dados
- Modelo normalizado de observação do mercado
- Estrutura inicial de engenharia de características
- Modelo de pontuação determinístico para referência
- Base para rotulagem e backtesting
- Configuração por variáveis de ambiente
- Verificações automatizadas com GitHub Actions
- Separação entre pesquisa, previsão, risco e execução
- Coleta de dados da CoinMarketCap
- Persistência no Firebase Realtime Database

## Arquitetura

```text
Fontes de dados
    |
    v
Aquisição -> Normalização -> Armazenamento
                              |
                              v
                  Engenharia de características
                              |
                              v
                       Modelo / Baseline
                              |
                    +---------+---------+
                    |                   |
                    v                   v
                 Avaliação          Filtro de risco
                    |                   |
                    +---------+---------+
                              v
                         Paper Trading
                              |
                              v
                       Execução futura
```

## Princípios de desenvolvimento

1. Nenhuma operação com dinheiro real nas versões iniciais.
2. Cada observação histórica deve representar somente informações disponíveis no instante da previsão, evitando vazamento de dados.
3. Modelos serão versionados e avaliados antes de serem promovidos.
4. A camada de risco poderá bloquear uma recomendação do modelo.
5. Dados brutos devem ser preservados sempre que possível para permitir a regeneração das características.
6. Segredos nunca são armazenados no repositório.

## Evolução planejada

- [x] Fundação do repositório
- [x] Arquitetura inicial de pesquisa
- [x] Contratos de dados
- [x] Modelo de pontuação de referência
- [x] Testes iniciais e CI
- [x] Cliente de aquisição da CoinMarketCap
- [x] Normalização dos snapshots
- [x] Adaptador de persistência Firebase
- [x] Workflow manual de coleta no GitHub Actions
- [ ] Coleta agendada do mercado
- [ ] Conector CoinGecko
- [ ] Construtor do dataset histórico
- [ ] Rotulagem de resultados 2x/5x/10x
- [ ] Modelo de Gradient Boosting
- [ ] Backtesting walk-forward
- [ ] Paper Trading
- [ ] Registro e regras de promoção de modelos
- [ ] Monitoramento em tempo real
- [ ] Adaptador de execução em corretora/exchange

## Desenvolvimento local

A camada de pesquisa e Machine Learning utiliza Python. A coleta da CoinMarketCap e a persistência no Firebase são implementadas como adaptadores independentes, permitindo adicionar novas fontes de dados e outros mecanismos de armazenamento sem acoplar o modelo a uma API específica.

```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
# macOS/Linux
# source .venv/bin/activate
pip install -r requirements.txt
pytest
```

Para configurar a aquisição, copie `.env.example` para `.env` e informe a URL do Firebase e o JSON da Service Account quando a persistência for necessária. Nunca faça commit de credenciais reais.
