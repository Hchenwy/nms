#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from django.core.exceptions import ValidationError


__all__ = ['init_model', 'generate_fake']


def init_model():
    from . import IDC, AssetGroup, Asset
    for cls in [IDC, AssetGroup, Asset]:
        if hasattr(cls, 'initial'):
            cls.initial()


def generate_fake():
    from . import IDC, AssetGroup, Asset
    for cls in [IDC, AssetGroup, Asset]:
        if hasattr(cls, 'generate_fake'):
            cls.generate_fake()

if __name__ == '__main__':
    pass