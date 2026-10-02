# Estudo de caso: controles de acesso nos laboratórios

## Problemas encontrados

O TechShop usava uma chave fixa para assinar tokens e permitia operações em `/api/users` sem autenticação. Isso permitia alterar ou excluir usuários sem verificar identidade e permissão. Os protótipos DevConnect e TaskFlow também expunham seu CRUD de usuários.

## Alterações

O TechShop agora exige uma chave pelo ambiente e restringe o CRUD administrativo a contas administradoras ativas com JWT válido. O cadastro público permanece em `/api/register`. Os protótipos usam um token administrativo de laboratório configurado pelo ambiente; não implementam contas individuais autenticadas. Também foram removidos debug automático e CORS universal no TechShop.

## Validação

Os testes usam bancos em memória e verificam acesso anônimo, conta comum, administrador, conta desativada e token assinado com outra chave. Testes dos protótipos verificam recusa quando a configuração está ausente ou o token está incorreto.

## Limitações

Esta é uma correção delimitada, não uma auditoria completa. A chave antiga continua no histórico Git; qualquer ambiente que a tenha usado precisa configurar uma chave nova, invalidando tokens antigos. Bancos já publicados não foram apagados. Dados reais eventualmente presentes exigem revisão separada. Não foram reescritas funcionalidades planejadas nem o histórico de commits.
