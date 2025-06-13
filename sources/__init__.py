from .base import SourceRegistry
from .github_trending import github_trending

# 注册信息源
SourceRegistry.register('github_trending', github_trending)

__all__ = ['SourceRegistry'] 