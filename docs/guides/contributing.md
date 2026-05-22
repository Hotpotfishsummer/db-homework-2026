# 贡献规范

## 分支命名

| 类型 | 格式 | 示例 |
|------|------|------|
| 新功能 | `features/xxx` | `features/ai-outfit-v2` |
| Bug 修复 | `bug-fix/xxx` | `bug-fix/login-redirect` |
| 文档 | `docs/xxx` | `docs/api-reference` |

## Commit 格式

```
<type>: <subject>

feat: add new outfit recommendation flow
fix: correct weather API fallback
docs: update README
style: format code
refactor: extract wardrobe repository
test: add user repository tests
chore: update dependencies
```

**type 分类：**
- `feat` — 新功能
- `fix` — Bug 修复
- `docs` — 文档更新
- `style` — 代码格式（不影响功能）
- `refactor` — 重构
- `test` — 测试相关
- `chore` — 构建/工具类

## PR 流程

1. 从 `main` 创建分支
2. 开发完成后，PR 标题简明扼要
3. Squash and merge 到 main
4. 删除已合并分支

## 分支同步

每日工作开始前：

```bash
git checkout main
git pull
git checkout your-branch
git rebase main
```

## 更多信息

详见 [CONTRIBUTING.md](../../CONTRIBUTING.md)