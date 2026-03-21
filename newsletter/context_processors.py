"""
Контекст-процессор для шаблонов: добавляет user_is_manager (флаг «пользователь — менеджер»).
"""

from .mixins import is_manager


def newsletter_context(request):
    """Добавляет в контекст шаблона user_is_manager для отображения меню и кнопок менеджера."""
    return {
        "user_is_manager": (
            is_manager(request.user) if request.user.is_authenticated else False
        )
    }
