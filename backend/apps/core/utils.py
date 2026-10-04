import hashlib
import secrets
import django.utils.text import slugify

def generate_unique_slug(model, value, field='slug', max_length=50):
    """
    Generate a unique slug for the given model and value.
    """
    base = slugify(value)[:max_length] or "org"
    slug = base
    n = 2
    while model.objects.filter(**{field: slug}).exists():
        suffix = f"-{n}"
        slug = base[:max_length - len(suffix)] + suffix
        n += 1
    return slug

def generate_token(nbytes=32):
    """
    Generate a random token of the specified number of bytes.
    """
    return secrets.token_urlsafe(nbytes)


def hash_token(token):
    """
    Hash the given token using SHA-256.
    """
    return hashlib.sha256(token.encode()).hexdigest()

def get_client_ip(request):
    """
    Get the client's IP address from the request.
    """
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')
