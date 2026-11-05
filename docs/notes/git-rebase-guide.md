# Guia de Atualização de Branch com Git Rebase

Este guia documenta o padrão adotado no repositório para atualizar branches de funcionalidade (*feature branches*) em relação à branch principal `develop` mantendo o histórico de commits limpo e linear.

---

## Sumário

- [1. Passo a Passo](#1-passo-a-passo)
   - [1.1. Atualizar a develop Local](#11-atualizar-a-develop-local)
   - [1.2. Iniciar o Rebase na sua Branch](#12-iniciar-o-rebase-na-sua-branch)
   - [1.3. Resolução de Conflitos](#13-resolução-de-conflitos)      
- [2. Publicar a Branch Atualizada](#2-publicar-a-branch-atualizada)
- [3. Alternativa: Atualizar Branch pelo GitHub Via Interface Web](#3-alternativa-atualizar-branch-pelo-github-via-interface-web)

---

## 1. Passo a Passo

### 1.1. Atualizar a `develop` Local

Antes de iniciar o rebase, garanta que sua base local reflete a versão mais recente da branch  remota:

```bash
git checkout develop
git pull origin develop

```

### 1.2. Iniciar o Rebase na sua Branch

Volte para a sua branch de trabalho e aplique os commits no topo da `develop` atualizada:

```bash
git checkout sua-branch
git rebase develop

```

**O que acontece aqui?** O Git desfaz temporariamente os seus commits, atualiza sua branch com a `develop` e reaplica suas alterações commit por commit.

---

### 1.3. Resolução de Conflitos 

Se o Git encontrar alterações conflitantes no mesmo trecho de código, o rebase será pausado.

1. **Abra o arquivo apontado com conflito no seu IDE.**
2. **Escolha a opção adequada nos marcadores de conflito:**
   * **Accept Both Changes:** Mantém as alterações vindas da `develop` e o seu código (recomendado quando ambas as lógicas se complementam).
   * **Accept Current Change:** Mantém o código vindo da `develop`.
   * **Accept Incoming Change:** Mantém a sua alteração da branch.

3. **Revise, ajuste e salve o arquivo.**

Após salvar as correções no arquivo:

```bash
# 1. Adiciona o arquivo resolvido à staging area
git add <caminho-do-arquivo>

# 2. Continua o processo de rebase
git rebase --continue

```
>[!WARNING]
>Não faça `git commit` durante o rebase: Ao resolver conflitos, utilize apenas `git add` e `git rebase --continue`.

>[!NOTE]
>Se a sua branch tiver múltiplos commits conflitantes, o rebase pausará novamente para o commit seguinte. Repita o processo até finalizar.

Se o processo de conflitos ficar confuso ou algo der errado, cancele tudo e volte ao estado inicial a qualquer momento com:

```bash
  git rebase --abort
```

---

## 2. Publicar a Branch Atualizada

Como o `rebase` reescreve a árvore de commits locais, a atualização no repositório remoto exige o push forçado. Utilize sempre a flag `--force-with-lease` para garantir que você não sobrescreva commits de terceiros por engano:

```bash
git push origin sua-branch --force-with-lease

```

---

## 3. Alternativa: Atualizar Branch pelo GitHub via Interface Web

Se a sua branch estiver apenas desatualizada em relação à `develop` e você preferir não usar o terminal para o rebase, o próprio GitHub oferece um recurso integrado na página do Pull Request:

1. Acesse o seu Pull Request no GitHub.

2. Role até a parte inferior onde aparecem as verificações de merge.

3. Se houver o botão **Update branch**, clique na seta ao lado do botão e selecione a opção **Update With Rebase**.

>[!WARNING]
>Não clique no botão **Update branch**, pois ele faz merge por padrão com os commits mais recentes da `develop`.

4. Seguindo esses passos, o GitHub fará a atualização da `develop` na sua branch automaticamente.

>Se o GitHub detectar conflitos que não consegue resolver sozinho, ele avisará que a resolução manual via terminal (seguindo os itens 1 e 2 acima) será necessária.
