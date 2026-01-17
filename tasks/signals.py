from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Epic, UserStory, Task
from .tasks import send_status_change_email

'''
User Updates Epic Status → Django saves to database → Signal fires → Email task triggered
'''


# Track old status values
def get_old_instance(model_class, instance):
    """Get the old instance from database before save"""
    try:
        return model_class.objects.get(pk=instance.pk)
    except model_class.DoesNotExist:
        return None


@receiver(pre_save, sender=Epic)
def epic_pre_save(sender, instance, **kwargs):
    """Store old status before Epic is saved"""
    if instance.pk:
        old_instance = get_old_instance(Epic, instance)
        if old_instance:
            instance._old_status = old_instance.status
        else:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Epic)
def epic_post_save(sender, instance, created, **kwargs):
    """Send email if Epic status changed"""
    if not created and hasattr(instance, '_old_status'):
        old_status = instance._old_status
        new_status = instance.status

        if old_status and old_status != new_status:
            # Trigger async task
            send_status_change_email.delay(
                model_name='Epic',
                instance_id=instance.id,
                old_status=old_status,
                new_status=new_status
            )


@receiver(pre_save, sender=UserStory)
def userstory_pre_save(sender, instance, **kwargs):
    """Store old status before UserStory is saved"""
    if instance.pk:
        old_instance = get_old_instance(UserStory, instance)
        if old_instance:
            instance._old_status = old_instance.status
        else:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=UserStory)
def userstory_post_save(sender, instance, created, **kwargs):
    """Send email if UserStory status changed"""
    if not created and hasattr(instance, '_old_status'):
        old_status = instance._old_status
        new_status = instance.status

        if old_status and old_status != new_status:
            send_status_change_email.delay(
                model_name='UserStory',
                instance_id=instance.id,
                old_status=old_status,
                new_status=new_status
            )


@receiver(pre_save, sender=Task)
def task_pre_save(sender, instance, **kwargs):
    """Store old status before Task is saved"""
    if instance.pk:
        old_instance = get_old_instance(Task, instance)
        if old_instance:
            instance._old_status = old_instance.status
        else:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Task)
def task_post_save(sender, instance, created, **kwargs):
    """Send email if Task status changed"""
    if not created and hasattr(instance, '_old_status'):
        old_status = instance._old_status
        new_status = instance.status

        if old_status and old_status != new_status:
            send_status_change_email.delay(
                model_name='Task',
                instance_id=instance.id,
                old_status=old_status,
                new_status=new_status
            )
