"""
页面模块 - 各个独立页面
"""
from .reviewer_config_page import ReviewerConfigPage
from .translation_settings_page import TranslationSettingsPage
from .api_manager_page import ApiManagerPage
from .quick_start_page import QuickStartPage
from .about_page import AboutPage

__all__ = [
    "ReviewerConfigPage",
    "TranslationSettingsPage",
    "ApiManagerPage",
    "QuickStartPage",
    "AboutPage",
]
