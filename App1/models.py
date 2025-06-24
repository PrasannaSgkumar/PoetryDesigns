from django.db import models
from decimal import Decimal
from django.utils import timezone

from django.db import models
from django.contrib.auth.hashers import make_password

class SuperAdmin(models.Model):
    username = models.CharField(max_length=200, unique=True)
    password = models.CharField(max_length=200, null=False)
    first_name = models.CharField(max_length=200, null=False)
    last_name = models.CharField(max_length=200, null=False)
    email = models.EmailField(max_length=200, null=False, unique=True)
    mobile_number = models.CharField(max_length=200, null=False, unique=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'super_admin'

    def save(self, *args, **kwargs):
       
        if not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super(SuperAdmin, self).save(*args, **kwargs)

    def __str__(self):
        return self.username


class Departments(models.Model):
    name=models.CharField(max_length=200, null=False, unique=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        db_table='departments'

    def __str__(self):
        return self.name
    
class Roles(models.Model):
    name=models.CharField(max_length=200, null=False, unique=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        db_table='roles'

    def __str__(self):
        return self.name

class users(models.Model):
    first_name=models.CharField(max_length=200, null=False)
    last_name=models.CharField(max_length=200, null=False)
    username=models.CharField(max_length=200, null=False, unique=True)
    email=models.EmailField(max_length=200, null=False, unique=True)
    mobile_number=models.CharField(max_length=200, null=False, unique=True)
    password=models.CharField(max_length=200, null=False)
    department=models.ForeignKey(Departments, on_delete=models.CASCADE, null=True)
    role=models.ForeignKey(Roles, on_delete=models.CASCADE, null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        db_table='users'

    def save(self, *args, **kwargs):
       
        if not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super(users, self).save(*args, **kwargs)

    def __str__(self):
        return self.first_name + ' ' + self.last_name
    

class Clients(models.Model):
    first_name=models.CharField(max_length=200, null=False)
    last_name=models.CharField(max_length=200, null=False)
    email=models.EmailField(max_length=200, null=False, unique=True)
    mobile_number=models.CharField(max_length=200, null=False, unique=True)
    username=models.CharField(max_length=200, null=False, unique=True)
    password=models.CharField(max_length=200, null=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    
    document_type = models.CharField(max_length=100, choices=[
        ('AADHAR', 'Aadhar'),
        ('PAN', 'PAN Card'),
        ('PASSPORT', 'Passport'),
        ('OTHER', 'Other'),
    ], null=True, blank=True)
    document_file = models.FileField(null=True, blank=True)
    document_number=models.CharField(unique=True, null=True, max_length=100)


    class Meta:
        db_table='clients'
    
    def save(self, *args, **kwargs):
       
        if not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super(Clients, self).save(*args, **kwargs)

    def __str__(self):
        return self.username


class TypesOfHouse(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class SupportingImages(models.Model):
    type_house = models.ForeignKey(TypesOfHouse, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='house_images/')

    def __str__(self):
        return f"Image for {self.type_house.name}"


class Project(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Ongoing', 'Ongoing'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    project_name = models.CharField(max_length=255)
    project_id=models.CharField(max_length=255, null=True, blank=True)
    design_phase_completed=models.BooleanField(default=False)
    construction_phase_completed=models.BooleanField(default=False)
    customer=models.ForeignKey(Clients, on_delete=models.CASCADE, null=True, blank=True)
    project_type = models.CharField(max_length=100)
    project_location = models.CharField(max_length=255)
    project_description = models.TextField(blank=True, null=True)
    project_dimensions = models.CharField(max_length=100, blank=True, null=True)

   
    type_of_house = models.ForeignKey(TypesOfHouse, on_delete=models.SET_NULL, null=True, blank=True)

    designed_file = models.FileField(upload_to='designs/', blank=True, null=True)
    preferred_file_format = models.CharField(max_length=50, blank=True, null=True)
    estimation_budget = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)

    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)

    original_contract_amount = models.DecimalField(max_digits=15, decimal_places=2)
    approved_changes_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))

   
    @property
    def current_total_amount(self):
        return self.original_contract_amount + self.approved_changes_amount

    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    user = models.ForeignKey(users, on_delete=models.SET_NULL, null=True, related_name='projects_created')
    checklist_doc = models.FileField(upload_to='checklists/', blank=True, null=True)

    inspected_by = models.ForeignKey(users, on_delete=models.SET_NULL, null=True, related_name='projects_inspected')
    inspection_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.project_name
    


class ConstructionStage(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    house_type = models.ForeignKey(TypesOfHouse, on_delete=models.CASCADE)
    sequence=models.IntegerField(unique=True)

    def __str__(self):
        return f"{self.name} - {self.house_type.name}"
    

class ConstructionDetail(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    stage = models.ForeignKey(ConstructionStage, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    start_date=models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    payment_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    payment_status = models.CharField(max_length=50, default='Pending')  
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    payment_date = models.DateField(blank=True, null=True)
   

    def __str__(self):
        return f"Stage: {self.stage.name} | Project: {self.project.name}"
    

class leads(models.Model):
    first_name=models.CharField(max_length=50, null=False)
    last_name=models.CharField(max_length=50, null=False)
    email=models.EmailField(unique=True)
    phone_number=models.BigIntegerField(null=False, unique=True)
    location=models.CharField(null=False, max_length=100)
    dimension=models.CharField(null=False, max_length=50)


class MinutesofMeeting(models.Model):
    project_id=models.ForeignKey(Project, on_delete=models.CASCADE)
    meeting_title=models.CharField(max_length=255)
    datetime=models.DateTimeField(null=False)
    attended_by=models.TextField()
    attachment=models.FileField(null=True, blank=True)
    notes=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    type=models.CharField(max_length=255, null=False, default="Online")

class Design(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='designs', null=False)
    customer = models.ForeignKey(Clients, on_delete=models.CASCADE, related_name='designs', null=False)
    is_new_design = models.BooleanField(default=True)
    design_2D = models.ImageField(upload_to='designs/2d/', null=False)
    design_3D = models.ImageField(upload_to='designs/3d/', null=False)

    def __str__(self):
        return f"Design for Project: {self.project.name} by Customer: {self.customer.name}"
    
class Projectteam(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    team_member = models.ForeignKey(users, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Project_Documents(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    document = models.FileField()
    name = models.CharField(max_length=255, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PasswordResetCode(models.Model):
    username = models.CharField(max_length=200)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=10)