# Git 协同规范

## 分支管理

| 分支 | 说明 | 备注 |
|------|------|------|
| `main` | 主分支 | 受保护，禁止直接 push |
| `features/` | 功能分支 | 如 `features/user-login` |
| `bug-fix/` | 修复分支 | 如 `bug-fix/login-crash` |
| `issue/` | 问题修复 | 如 `issue/123-login-error` |
| 其他 | 按需创建 | 如 `dev/`, `test/` 等 |

### 分支所有权

- **不要直接修改他人的分支**：所有改动应通过 PR 提交，除非获得分支所有者授权
- **如需协助修复**：可以通过以下方式：
  1. 在分支上开新分支，提交 PR 到他人的分支
  2. 告知分支所有者需要修改的内容，由其自行提交
  3. 在获得明确授权后，才能直接在他人分支上提交
- **紧急情况**：如果需要在他人分支上直接修改（如 hotfix），必须通知所有者并在事后说明

## 提交规范

### 格式
```
<type>: <subject>

[可选 body]

[可选 footer]
```

### Type 类型
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具相关

### 示例
```
feat: 添加用户登录功能

- 添加登录表单组件
- 集成后端登录 API
```

## Pull Request 流程

### 详细步骤

#### 1. 创建分支
```bash
# 确保 main 最新
git checkout main
git pull origin main

# 创建功能分支
git checkout -b features/user-login
```

#### 2. 开发与提交
```bash
# 提交时使用规范的 commit message
git add .
git commit -m "feat: 添加用户登录表单组件"
```

#### 3. 推送远程
```bash
# 首次推送需要设置 upstream
git push -u origin features/user-login

# 后续直接
git push
```

#### 4. 创建 PR
1. 在 GitHub 仓库页面点击 **New pull request**
2. 选择源分支（你的功能分支）和目标分支（main）
3. 填写 PR 描述（见下方模板）
4. 指定 reviewer

#### 5. 代码 Review
- reviewer 在 PR 页面提出修改意见
- 作者根据意见修改后，在评论区回复已处理
- 重复直到获得 approve

#### 6. 合并与清理
```bash
# reviewer 点击 Merge 后，本地可删除分支
git checkout main
git pull origin main        # 同步最新代码
git branch -d features/user-login    # 删除本地分支
git push origin --delete features/user-login  # 删除远程分支（可选）
```

### PR 描述模板

```markdown
## 概述
[简要描述本次 PR 做了什么]

## 改动内容
- [改动点 1]
- [改动点 2]

## 涉及文件
- `src/pages/Login.vue`
- `api/auth.js`

## 测试方式
1. 打开页面 `/login`
2. 输入账号密码点击登录
3. 验证跳转到首页

## 相关 Issue
Closes #123
```

## 粒度管理

### 提交粒度
- **一个提交只做一件事**：添加功能、修复 bug、修改样式等分开提交
- **避免超大提交**：单次提交不超过 500 行改动的文件
- **及时提交**：不要等到写完整个功能再提交，完成一个子功能即可提交

### PR 粒度
- **PR 应该小巧**：建议不超过 10 个文件或 500 行改动
- **一个 PR 只解决一个问题**：不要在一个 PR 里混合多个不相关的改动
- **拆分大功能**：如果功能较大，拆分成多个小 PR 依次提交

### 粒度把控原则
| 情况 | 建议 |
|------|------|
| PR 超过 10 个文件 | 考虑拆分 |
| 提交信息难以简短描述 | 考虑拆分 |
| Review 时间超过 30 分钟 | 考虑拆分 |
| 出现不相关的改动 | 拆分成独立提交 |

### 示例
```
# 好的实践
features/user-login          # 1-3 个文件，小而精
features/add-auth-api        # 独立功能，可单独 review

# 不好的实践
features/user-system         # 登录+注册+权限+...太大
features/lots-of-changes     # 无法描述清楚改了什么
```

## Pull Request 合并方式

### 推荐：Merge（合并 commit）

**为什么推荐 merge：**
- 保留完整的提交历史，可以看到所有分支的演进过程
- 如果出问题，易于回溯特定提交
- 团队成员不需要了解复杂的 rebase 操作
- GitHub PR 界面直接支持，一键合并

```bash
# GitHub 上点击 "Merge pull request" 按钮
# 等同于以下命令
git checkout main
git merge features/user-login
```

**Merge 风格选择：** 建议使用 **Squash and merge**（压缩合并）
- 把一个分支的多个提交压缩成一个 commit 合并到 main
- 保持 main 历史整洁，每个功能/修复只对应一个 commit
- 适合功能分支开发过程中有多次调试提交的情况

```bash
# Squash and merge 示例
# 假设 features/user-login 有 5 个 commit
# 合并后 main 上只有一个 commit
# commit message 可以自定义
```


### 规范

| 操作 | 方式 | 说明 |
|------|------|------|
| PR 合并到 main | **Squash and merge** | 压缩多个提交，保持历史整洁 |
| 同步 main 到功能分支 | **rebase** | 保持功能分支历史线性 |

---

## 分支同步（开发者日常工作）

### 场景一：每天开始工作前

```bash
# 1. 切换到 main
git checkout main

# 2. 拉取最新代码（推荐）
git pull --rebase origin main

# 3. 切换回你的功能分支
git checkout features/your-branch

# 4. 把 main 的最新变更同步过来（推荐 rebase）
git rebase main

# 如果你的分支已经 push 到远程，使用
git rebase origin/main
```

### 场景二：功能分支开发过程中 main 有更新

```bash
# 方法一：rebase（推荐）
git fetch origin
git rebase origin/main

# 方法二：merge（如果 rebase 复杂或有冲突）
git fetch origin
git merge origin/main
```

### 场景三：rebase 过程中遇到冲突

```bash
# 1. 查看冲突文件
git status

# 2. 编辑冲突文件，解决冲突
# 冲突标记格式：
# <<<<<<< HEAD
# 你的代码
# =======
# main 上的代码
# >>>>>>>

# 3. 标记冲突已解决
git add <冲突文件>

# 4. 继续 rebase
git rebase --continue

# 如果冲突太多难以处理，可以放弃
git rebase --abort
```

### 同步原则

- **每天开始工作前**：先同步 main，再开始开发
- **提交 PR 前**：确保功能分支是基于最新的 main
- **避免长期不 sync**：超过 3 天的分支容易产生大量冲突
- **冲突不可怕**：及时沟通，小步同步比攒大量冲突好处理

---

## 分支清理

### 合并完成后删除分支

#### 1. GitHub 上删除（推荐）

在 PR 合并页面，点击 **"Delete branch"** 按钮即可同时删除远程分支。

#### 2. 命令行删除

```bash
# 删除本地分支
git checkout main                  # 先切换到 main
git branch -d features/user-login  # 删除本地分支

# 强制删除（如果分支还没合并）
git branch -D features/user-login

# 删除远程分支
git push origin --delete features/user-login
```

### 清理已删除的远程分支引用

```bash
# 删除了远程分支后，本地会保留一个过时引用
git fetch origin --prune
# 或者
git remote prune origin
```

### 日常分支维护

```bash
# 查看已合并到 main 的分支
git branch --merged main

# 批量删除已合并的本地分支
git branch --merged main | grep -v "main" | xargs -n 1 git branch -d

# 查看所有分支（本地 + 远程）
git branch -a
```

### 清理原则

- **PR 合并后立即删除**：不要保留已完成工作的分支
- **定期执行 prune**：清理远程已删除分支的本地引用
- **保持分支列表整洁**：执行 `git branch` 时只看到正在使用的分支

---

## Gitignore 规范

### 基本要求

**必须有 `.gitignore` 文件**，且必须忽略以下类型的文件：

| 类型 | 示例 | 原因 |
|------|------|------|
| 依赖目录 | `node_modules/`、`env/`、Conda 环境 | 体积大，可通过安装脚本重新生成 |
| 构建产物 | `dist/`、`build/`、`.pyc`、`.pyo` | 由源码生成，不需要同步 |
| 本地测试/调试文件 | `.pytest_cache/`、`__pycache__/`、`.coverage` | 本地开发产物，无意义 |
| IDE/编辑器配置 | `.idea/`、`.vscode/`、`.DS_Store` | 个人环境差异，无需同步 |
| 环境变量文件 | `.env`、`.env.local` | 可能包含敏感信息 |
| 日志文件 | `*.log`、`logs/` | 本地调试产物 |
| 临时文件 | `*.tmp`、`*.swp` | 编辑器临时文件 |

### 本项目 .gitignore 示例

```gitignore
# 前端
frontend/node_modules/
frontend/dist/
frontend/.DS_Store

# 后端
backend/.pytest_cache/
backend/**/__pycache__/
backend/**/*.pyc
backend/*.pyo

# Python 虚拟环境
backend/env/
venv/

# IDE
.idea/
.vscode/
.DS_Store

# 环境变量（切勿提交！）
.env
.env.local
.env.*.local

# 日志
*.log
logs/

# 临时文件
*.tmp
*.swp
```

### 注意事项

- **不要提交 `node_modules/`** —— 运行 `npm install` / `pip install` 即可重新安装
- **不要提交 `.env`** —— 如果需要环境变量模板，创建一个 `.env.example` 供参考
- **不要提交 IDE 配置** —— 保持仓库对所有人一致
- **不要提交构建产物** —— `dist/`、`build/` 等由源码生成

### 如果误提交了

```bash
# 1. 从 git 移除（但保留本地文件）
git rm -r --cached node_modules/

# 2. 提交更改
git commit -m "chore: remove node_modules from tracking"

# 3. 推送后其他成员需要重新拉取
```

### 验证方法

```bash
# 查看即将提交的文件（检查是否有遗漏）
git status

# 确保没有 node_modules、dist、__pycache__ 等
```

---

## 其他规范

- 提交信息应清晰描述改了什么，便于追溯
- 每天工作开始前先 `git pull --rebase` 同步 main
- PR 描述应完整，便于 reviewer 理解改动目的
- 合并后及时删除无用分支，保持仓库整洁
- 必须包含 `.gitignore` 文件，忽略所有无意义的同步文件