from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Epic, UserStory, Task


@shared_task
def send_status_change_email(model_name, instance_id, old_status, new_status):
    """
    Send email notification when Epic/UserStory/Task status changes

    Args:
        model_name: 'Epic', 'UserStory', or 'Task'
        instance_id: ID of the changed instance
        old_status: Previous status
        new_status: New status
    """
    # Get the model class
    model_map = {
        'Epic': Epic,
        'UserStory': UserStory,
        'Task': Task,
    }

    model_class = model_map.get(model_name)
    if not model_class:
        return f"Invalid model name: {model_name}"

    try:
        instance = model_class.objects.get(id=instance_id)
    except model_class.DoesNotExist:
        return f"{model_name} with id {instance_id} not found"

    # Collect recipients
    recipients = []

    # Add owner/assigned_to email
    if hasattr(instance, 'owner') and instance.owner and instance.owner.email:
        recipients.append(instance.owner.email)
    elif hasattr(instance, 'assigned_to') and instance.assigned_to and instance.assigned_to.email:
        recipients.append(instance.assigned_to.email)

    # Add reporter email
    if instance.reporter and instance.reporter.email:
        recipients.append(instance.reporter.email)

    # Remove duplicates
    recipients = list(set(recipients))

    if not recipients:
        return "No recipients with valid email addresses"

    # Prepare email
    subject = f"{model_name} Status Changed: {instance.title}"
    message = f"""Hello,The status of {model_name} "{instance.title}" has been changed:Previous Status: {old_status}
    New Status: {new_status}                                                                                                                                                                                                     

      {model_name} Details:                                                                                                                                                                                                        
      - Title: {instance.title}                                                                                                                                                                                                    
      - Priority: {instance.priority}                                                                                                                                                                                              
      - Status: {new_status}                                                                                                                                                                                                       

      Best regards,                                                                                                                                                                                                                
      Task Manager System                                                                                                                                                                                                          
      """

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )
        return f"Email sent successfully to {', '.join(recipients)}"
    except Exception as e:
        return f"Failed to send email: {str(e)}"
