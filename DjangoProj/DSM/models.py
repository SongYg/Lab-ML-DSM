from __future__ import unicode_literals

from django.db import models

# Create your models here.


class Student(models.Model):
    """student table"""
    student_id = models.CharField(
        primary_key=True, max_length=50, default='-1')

    def __unicode__(self):
        return u'%s' % (self.student_id)


class Sequence(models.Model):
    """Sequence table"""
    sequence_id = models.CharField(
        primary_key=True, max_length=30, default='-1')
    sequence_name = models.CharField(max_length=50, default='-1')

    def __unicode__(self):
        return u'%s %s' % (self.sequence_id, self.sequence_name)


class Unit(models.Model):
    """Unit table"""
    unit_id = models.CharField(primary_key=True, max_length=30, default='-1')
    unit_name = models.CharField(max_length=100, default='-1')
    sequence = models.ForeignKey(Sequence)

    def __unicode__(self):
        return u'%s %s' % (self.unit_id, self.unit_name)


class Module(models.Model):
    """Module table"""
    module_id = models.CharField(primary_key=True, max_length=30, default='-1')
    module_name = models.CharField(max_length=10, default='-1')
    unit = models.ForeignKey(Unit)

    def __unicode__(self):
        return u'%s %s' % (self.module_id, self.module_name)


class Section(models.Model):
    """Section table"""
    section_id = models.CharField(
        primary_key=True, max_length=30, default='-1')
    section_name = models.CharField(max_length=100, default='-1')
    parent_type = models.CharField(max_length=10, default='-1')
    parent_id = models.CharField(max_length=30, default='-1')
    module = models.ForeignKey(Module)

    def __unicode__(self):
        return u'%s %s %s %s %s' % (self.section_id, self.section_name, self.parent_type, self.parent_id, self.module)


class Problem(models.Model):
    """Problem table"""
    problem_id = models.CharField(
        primary_key=True, max_length=30, default='-1')
    problem_name = models.CharField(max_length=50, default='-1')
    description = models.CharField(max_length=50, default='-1')
    learning_objectives = models.CharField(max_length=5000, default='-1')
    purpose = models.CharField(max_length=50, default='-1')
    module = models.ForeignKey(Module)

    def __unicode__(self):
        return u'%s %s %s %s %s' % (self.problem_id, self.problem_name, self.description, self.learning_objectives, self.purpose)


class Step(models.Model):
    step_id = models.CharField(primary_key=True, max_length=50, default='-1')
    step_name = models.CharField(max_length=100, default='-1')
    step_content = models.CharField(max_length=5000, default='-1')
    step_type = models.CharField(max_length=5, default='-1')
    value = models.CharField(max_length=5000, default='-1')
    problem = models.ForeignKey(Problem, null=True)
    kc1 = models.CharField(max_length=1000, default='-1')

    def __unicode__(self): return u'%s %s %s %s %s %s' % (self.step_id,
                                                          self.step_name, self.step_content, self.value)


class Feedback(models.Model):
    feedback_id = models.CharField(
        primary_key=True, max_length=50, default='-1')
    match = models.CharField(max_length=10, default='-1')
    score = models.IntegerField(default=0)
    correct = models.BooleanField(default=False)
    feedback_content = models.CharField(max_length=5000, default='-1')
    step = models.ForeignKey(Step)

    def __unicode__(self): return u'%s %s %s %s %s %s' % (self.feedback_id,
                                                          self.match, self.score, self.correct, self.feedback_content, self.step)


class Hint(models.Model):
    hint_id = models.CharField(primary_key=True, max_length=50, default='-1')
    hint_level = models.IntegerField(default=0)
    hint_content = models.CharField(max_length=5000, default='-1')
    step = models.ForeignKey(Step)

    def __unicode__(self): return u'%s %s %s %s' % (self.hint_id,
                                                    self.hint_level, self.hint_content, self.step)
