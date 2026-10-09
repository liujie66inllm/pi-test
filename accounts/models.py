from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """用户扩展资料：与内置 User 一对一关联，保存最高分等信息。"""
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile',
        verbose_name='用户'
    )
    high_score = models.IntegerField(default=0, verbose_name='贪吃蛇最高分')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='注册时间')

    class Meta:
        verbose_name = '用户资料'
        verbose_name_plural = '用户资料'

    def __str__(self):
        return f'{self.user.username} 的资料'


# 注册新用户时自动创建 Profile
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


# 保存用户时同步保存 Profile
@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
