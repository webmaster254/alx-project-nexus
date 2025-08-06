from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError


class Industry(models.Model):
    """
    Industry model for job industry classification.
    Used to categorize jobs by industry sector.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Industry name (e.g., Technology, Healthcare, Finance)"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the industry sector"
    )
    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True,
        help_text="URL-friendly version of industry name"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this industry is active for job classification"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'industry'
        verbose_name = 'Industry'
        verbose_name_plural = 'Industries'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Auto-generate slug from industry name if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def job_count(self):
        """Return the number of active jobs in this industry."""
        try:
            return self.job_set.filter(is_active=True).count()
        except AttributeError:
            return 0


class JobType(models.Model):
    """
    JobType model for employment type classification.
    Defines different types of employment arrangements.
    """
    EMPLOYMENT_TYPES = [
        ('full-time', 'Full-time'),
        ('part-time', 'Part-time'),
        ('contract', 'Contract'),
        ('temporary', 'Temporary'),
        ('internship', 'Internship'),
        ('freelance', 'Freelance'),
        ('remote', 'Remote'),
        ('hybrid', 'Hybrid'),
    ]

    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="Job type name (e.g., Full-time, Part-time, Contract)"
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        choices=EMPLOYMENT_TYPES,
        help_text="Standardized code for the job type"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the employment type"
    )
    slug = models.SlugField(
        max_length=70,
        unique=True,
        blank=True,
        help_text="URL-friendly version of job type name"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this job type is active for job classification"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'job_type'
        verbose_name = 'Job Type'
        verbose_name_plural = 'Job Types'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Auto-generate slug from job type name if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def job_count(self):
        """Return the number of active jobs of this type."""
        try:
            return self.job_set.filter(is_active=True).count()
        except AttributeError:
            return 0


class Category(models.Model):
    """
    Category model with hierarchical structure for job categorization.
    Supports parent-child relationships for nested categories.
    """
    name = models.CharField(
        max_length=100,
        help_text="Category name (e.g., Software Development, Marketing)"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the job category"
    )
    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True,
        help_text="URL-friendly version of category name"
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        help_text="Parent category for hierarchical structure"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this category is active for job classification"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'category'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']
        unique_together = ['name', 'parent']

    def __str__(self):
        """Return full category path for hierarchical display."""
        if self.parent:
            return f"{self.parent} > {self.name}"
        return self.name

    def clean(self):
        """Validate category to prevent circular references."""
        super().clean()
        if self.parent:
            # Check for circular reference
            if self._would_create_circular_reference():
                raise ValidationError("Category cannot be its own parent or create circular references.")
            
            # Check depth limit (max 3 levels)
            if self._get_depth() > 3:
                raise ValidationError("Category hierarchy cannot exceed 3 levels deep.")

    def save(self, *args, **kwargs):
        """Auto-generate slug from category name if not provided."""
        if not self.slug:
            base_slug = slugify(self.name)
            # Ensure unique slug by appending parent slug if exists
            if self.parent:
                self.slug = f"{self.parent.slug}-{base_slug}"
            else:
                self.slug = base_slug
            
            # Handle slug conflicts
            original_slug = self.slug
            counter = 1
            while Category.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        # Run validation before saving
        self.full_clean()
        super().save(*args, **kwargs)

    def _would_create_circular_reference(self):
        """Check if setting this parent would create a circular reference."""
        if not self.parent:
            return False
        
        # Check if parent is self
        if self.parent == self:
            return True
        
        # Check if any ancestor is self
        current = self.parent
        while current:
            if current == self:
                return True
            current = current.parent
        
        return False

    def _get_depth(self):
        """Calculate the depth of this category in the hierarchy."""
        depth = 1
        current = self.parent
        while current:
            depth += 1
            current = current.parent
        return depth

    def get_ancestors(self):
        """Return all ancestor categories from root to immediate parent."""
        ancestors = []
        current = self.parent
        while current:
            ancestors.insert(0, current)
            current = current.parent
        return ancestors

    def get_descendants(self):
        """Return all descendant categories (children, grandchildren, etc.)."""
        descendants = []
        
        def collect_descendants(category):
            for child in category.children.all():
                descendants.append(child)
                collect_descendants(child)
        
        collect_descendants(self)
        return descendants

    def get_root(self):
        """Return the root category of this hierarchy."""
        current = self
        while current.parent:
            current = current.parent
        return current

    def is_root(self):
        """Check if this category is a root category (has no parent)."""
        return self.parent is None

    def is_leaf(self):
        """Check if this category is a leaf category (has no children)."""
        return not self.children.exists()

    def get_level(self):
        """Return the level of this category (0 for root, 1 for first level, etc.)."""
        return self._get_depth() - 1

    def get_siblings(self):
        """Return all sibling categories (same parent)."""
        if self.parent:
            return Category.objects.filter(parent=self.parent).exclude(pk=self.pk)
        else:
            return Category.objects.filter(parent__isnull=True).exclude(pk=self.pk)

    @property
    def job_count(self):
        """Return the number of active jobs in this category and its descendants."""
        try:
            # Count jobs directly in this category
            direct_count = self.job_set.filter(is_active=True).count()
            
            # Count jobs in descendant categories
            descendant_count = 0
            for descendant in self.get_descendants():
                descendant_count += descendant.job_set.filter(is_active=True).count()
            
            return direct_count + descendant_count
        except AttributeError:
            return 0

    @property
    def full_path(self):
        """Return the full hierarchical path of this category."""
        path_parts = []
        current = self
        while current:
            path_parts.insert(0, current.name)
            current = current.parent
        return " > ".join(path_parts)
