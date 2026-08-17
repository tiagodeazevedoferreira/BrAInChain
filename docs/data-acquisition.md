# Aquisição de Dados V1

## CoinMarketCap

O coletor utiliza `GET /v3/cryptocurrency/listings/latest`. A CMC documenta esse endpoint como a rota atual de listagens de criptomoedas ativas. O coletor utiliza `CMC_API_KEY` quando disponível; sem uma chave, utiliza o endpoint de avaliação sem chave documentado pela CMC.

O primeiro esquema de snapshot captura intencionalmente os campos necessários para a futura engenharia de características:

- ID estável da CMC
- nome/símbolo/slug
- data de inclusão
- instante da captura
- ranking CMC
- preço e capitalização de mercado
- volume de 24h
- variações percentuais de 1h/24h/7d
- métricas de oferta
- quantidade de pares de mercado
- registro bruto original da CMC

O registro bruto é preservado porque características futuras podem exigir campos que ainda não foram modelados explicitamente.

## Firebase

O Firebase Realtime Database é o destino de persistência da camada de aquisição. As credenciais são fornecidas por variáveis de ambiente ou secrets do GitHub Actions. Nenhum JSON de Service Account é armazenado no repositório.

Os snapshots são gravados em:

```text
snapshots/<id-da-coinmarketcap>/<instante-da-captura>
```

Isso preserva a observação temporal necessária para a futura geração de rótulos e para o backtesting.

## Execução manual no GitHub Actions

O workflow `.github/workflows/collect-market.yml` é intencionalmente **manual na V1**. Isso evita consumo inesperado da API ou gravações no banco enquanto validamos credenciais e regras de retenção.

Secrets necessários no repositório GitHub:

- `CMC_API_KEY` (opcional enquanto utilizarmos o endpoint de avaliação)
- `FIREBASE_DATABASE_URL`
- `FIREBASE_CREDENTIALS_JSON`

Depois que o pipeline for validado, poderemos adicionar um acionamento agendado e definir a frequência de coleta de acordo com os limites da API e a granularidade necessária para o modelo.
