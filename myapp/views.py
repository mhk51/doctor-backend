from django.conf import settings
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView 
from rest_framework import viewsets
from .models import WhatsAppToken, Media, WhatsMessage,Recurrence, AttachmentReminder, ProcedureInstruction, GeneralHealthReminders, PatientEducation,Room, Message,Role, Event, Reference, Files, Clinic, VirtualMeet, Users, Patient, SocialMedia, SocialMediaAccount, Allergies, SpecialNeed, Diagnosis, Surgery, Vital, Prescription, Notes, Attachment, Insurance, PatientHasSurgery, PatientHasInsurance, PatientHasVital, PatientHasPrescription, PatientHasDiagnosis, Problem, PatientHasProblem, MedicalTest, Result, ReferralDoctors, PatientHasReferralDoctors, UsersHasReferralDoctors, UsersHasPatient, Templates, UsersHasTemplates, PatientReceiveTemplates, Appointment, Tasks, UsersHasTasks, RadiologyResult, RadiologyTest, Billing
from .serializers import WhatsAppTokenSerializer, MediaSerializer, WhatsMessageSerializer, PatientEducationSerializer, ProcedureInstructionSerializer, GeneralHealthRemindersSerializer, RecurrenceSerializer, AttachmentReminderSerializer, RoomSerializer, MessageSerializer, EventSerializer, ProfileUpdateSerializer, UserRegistrationSerializer, RoleSerializer,ReferenceSerializer, FilesSerializer, ClinicSerializer, VirtualMeetSerializer, UsersSerializer, PatientSerializer, SocialMediaSerializer, SocialMediaAccountSerializer, AllergiesSerializer, SpecialNeedSerializer, DiagnosisSerializer, SurgerySerializer, VitalSerializer, PrescriptionSerializer, NotesSerializer, AttachmentSerializer, InsuranceSerializer, PatientHasSurgerySerializer, PatientHasInsuranceSerializer, PatientHasVitalSerializer, PatientHasPrescriptionSerializer, PatientHasDiagnosisSerializer, ProblemSerializer, PatientHasProblemSerializer, MedicalTestSerializer, ResultSerializer, ReferralDoctorsSerializer,PatientHasReferralDoctorsPostSerializer,PatientHasReferralDoctorsGetSerializer, UsersHasReferralDoctorsSerializer, UsersHasPatientSerializer, TemplatesSerializer, UsersHasTemplatesSerializer, PatientReceiveTemplatesSerializer, AppointmentSerializer, TasksSerializer, UsersHasTasksSerializer, RadiologyTestSerializer, RadiologyResultSerializer, BillingSerializer
from django.http import JsonResponse
from rest_framework.generics import RetrieveUpdateAPIView
from django.http import HttpResponse, JsonResponse
from rest_framework import generics
from django.http import FileResponse
from django.http import Http404
from django.shortcuts import get_object_or_404
import subprocess
from django.shortcuts import redirect
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.filters import SearchFilter
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from rest_framework.authentication import TokenAuthentication
from django.db.models import Q,F, Value as V
from django.db.models.functions import Concat


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Recurrence

@api_view(['GET'])
def get_recurrence_and_template(request, idrecurrence=None):
    try:
        if idrecurrence is not None:
            # Fetch the specific recurrence and template based on idrecurrence
            recurrence = Recurrence.objects.select_related('templateID').get(idrecurrence=idrecurrence)

            # Access fields from both models
            result = {
                'idrecurrence': recurrence.idrecurrence,
                'send': recurrence.send,
                'appointment': recurrence.appointment,
                'type': recurrence.type,
                'occurrence': recurrence.occurrence,
                'templateID': {
                    'idTemplates': recurrence.templateID.idTemplates,
                    'name': recurrence.templateID.name,
                    'type': recurrence.templateID.type,
                    'subType': recurrence.templateID.subType,
                    'body': recurrence.templateID.body,
                    'expire': recurrence.templateID.expire,
                }
            }

            return Response({'result': result}, status=status.HTTP_200_OK)
        else:
            # Fetch all recurrences and templates
            queryset = Recurrence.objects.select_related('templateID')

            # Access fields from both models
            result = list(queryset.values(
                'idrecurrence',         # Recurrence model fields
                'send',
                'appointment',
                'type',
                'occurrence',
                'templateID__idTemplates',  # Access fields from the related Templates model
                'templateID__name',
                'templateID__type',
                'templateID__subType',
                'templateID__body',
                'templateID__expire'
            ))

            return Response({'result': result}, status=status.HTTP_200_OK)

    except Recurrence.DoesNotExist:
        # Return a 404 response if the recurrence is not found
        return Response({'error': 'Recurrence not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        # Handle other exceptions, log them, and return an appropriate response
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

class UsersViewSet(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def list(self, request, *args, **kwargs):
        if 'all' in request.query_params:
            return super().list(request, *args, **kwargs)
        else:
            user = request.user
            serializer = self.get_serializer(user)
            return Response(serializer.data)

@api_view(['POST'])
def verify_password(request):
    # Get the user's old password from the request
    old_password = request.data.get('old_password')

    # Get the authenticated user
    user = request.user

    # Check if the old password matches the user's current password
    if user.check_password(old_password):
        return Response({'success': True, 'message': 'Password verified successfully'})
    else:
        return Response({'success': False, 'message': 'Old password does not match'}, status=status.HTTP_400_BAD_REQUEST)

class ProfileUpdateView(generics.UpdateAPIView):
    queryset = Users.objects.all()  # Assuming Users is the model for user profiles
    serializer_class = ProfileUpdateSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    

class ProfileView(RetrieveUpdateAPIView):
    serializer_class = ProfileUpdateSerializer
    queryset = Users.objects.all()
    lookup_field = 'email'  # Assuming email is used to identify the user

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserRegistration(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def logout_view(request):
    # Log the user out
    logout(request)
    return Response({"message": "User logged out successfully"})

@api_view(['POST'])
def custom_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(request, username=username, password=password)

    if user:
        # If the user is valid, log them in
        login(request, user)
        print("user", user)
        # Generate or get the token for the user
        token, created = Token.objects.get_or_create(user=user)
        user_role = user.role_idrole  # Assuming 'user.role_roleid' is a foreign key to the 'Role' model
        role_name = user_role.name  # Access the 'name' field of the 'Role' model
        print ("user toke", token.user)
        return Response({'token': token.key, 'role': role_name})
    else:
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@permission_classes([IsAuthenticated])       
@api_view(['GET'])
def rooms(request):
    user = request.user
    role_name = user.role_idrole.name if user.role_idrole else None
    print(f'User: {user.email}, Role: {role_name}')
    if role_name in ['Nurse', 'Secretary']:
        rooms = Room.objects.filter(name=f'Room for {user.email}')
    else:
        rooms = Room.objects.all()

    serializer = RoomSerializer(rooms, many=True)
    return Response({'rooms': serializer.data})

@permission_classes([IsAuthenticated])
@api_view(['GET'])
def room(request, id):
    print(f"room")
    room = get_object_or_404(Room, pk=id)
    messages = Message.objects.filter(room=room)
    print(f'request: {request}')
    room_serializer = RoomSerializer(room)
    message_serializer = MessageSerializer(messages, many=True)
    return Response({'room': room_serializer.data, 'messages': message_serializer.data})       

class AllUsersListView(APIView):
    def get(self, request):
        users = Users.objects.all()
        serializer = UsersSerializer(users, many=True)
        return Response(serializer.data)

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    filter_backends = [SearchFilter]
    search_fields = ['first_name', 'last_name']
    
    #search for patient by name (to be used later)
    # def get_queryset(self):
    #     query = self.request.query_params.get('query', None)
    #     if query:
    #         queryset = Patient.objects.annotate(
    #             full_name=Concat(F('first_name'), V(' '), F('last_name'))
    #         ).filter(
    #             Q(full_name__icontains=query)
    #         )
    #         return queryset
    #     return super().get_queryset()

class WhatsAppTokenViewSet(viewsets.ModelViewSet):
    queryset = WhatsAppToken.objects.all()
    serializer_class = WhatsAppTokenSerializer

class SocialMediaViewSet(viewsets.ModelViewSet):
    queryset = SocialMedia.objects.all()
    serializer_class = SocialMediaSerializer

class SocialMediaAccountViewSet(viewsets.ModelViewSet):
    queryset = SocialMediaAccount.objects.all()
    serializer_class = SocialMediaAccountSerializer
    http_method_names = ['get', 'post', 'put', 'delete'] 

class ProcedureInstructionViewSet(viewsets.ModelViewSet):
    queryset = ProcedureInstruction.objects.all()
    serializer_class = ProcedureInstructionSerializer

class PatientEducationViewSet(viewsets.ModelViewSet):
    queryset = PatientEducation.objects.all()
    serializer_class = PatientEducationSerializer

class GeneralHealthRemindersViewSet(viewsets.ModelViewSet):
    queryset = GeneralHealthReminders.objects.all()
    serializer_class = GeneralHealthRemindersSerializer

class AllergiesViewSet(viewsets.ModelViewSet):
    queryset = Allergies.objects.all()
    serializer_class = AllergiesSerializer

class SpecialNeedViewSet(viewsets.ModelViewSet):
    queryset = SpecialNeed.objects.all()
    serializer_class = SpecialNeedSerializer

class DiagnosisViewSet(viewsets.ModelViewSet):
    queryset = Diagnosis.objects.all()
    serializer_class = DiagnosisSerializer

class SurgeryViewSet(viewsets.ModelViewSet):
    queryset = Surgery.objects.all()
    serializer_class = SurgerySerializer

class VitalViewSet(viewsets.ModelViewSet):
    queryset = Vital.objects.all()
    serializer_class = VitalSerializer

class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer

class NotesViewSet(viewsets.ModelViewSet):
    queryset = Notes.objects.all()
    serializer_class = NotesSerializer

class AttachmentViewSet(viewsets.ModelViewSet):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer
    
class InsuranceViewSet(viewsets.ModelViewSet):
    queryset = Insurance.objects.all()
    serializer_class = InsuranceSerializer

class PatientHasSurgeryViewSet(viewsets.ModelViewSet):
    queryset = PatientHasSurgery.objects.all()
    serializer_class = PatientHasSurgerySerializer

class PatientHasInsuranceViewSet(viewsets.ModelViewSet):
    queryset = PatientHasInsurance.objects.all()
    serializer_class = PatientHasInsuranceSerializer

class PatientHasVitalViewSet(viewsets.ModelViewSet):
    queryset = PatientHasVital.objects.all()
    serializer_class = PatientHasVitalSerializer

class PatientHasPrescriptionViewSet(viewsets.ModelViewSet):
    queryset = PatientHasPrescription.objects.all()
    serializer_class = PatientHasPrescriptionSerializer

class PatientHasDiagnosisViewSet(viewsets.ModelViewSet):
    queryset = PatientHasDiagnosis.objects.all()
    serializer_class = PatientHasDiagnosisSerializer

class ProblemViewSet(viewsets.ModelViewSet):
    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer

class PatientHasProblemViewSet(viewsets.ModelViewSet):
    queryset = PatientHasProblem.objects.all()
    serializer_class = PatientHasProblemSerializer

class MedicalTestViewSet(viewsets.ModelViewSet):
    queryset = MedicalTest.objects.all()
    serializer_class = MedicalTestSerializer

class ResultViewSet(viewsets.ModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer

class ReferralDoctorsViewSet(viewsets.ModelViewSet):
    queryset = ReferralDoctors.objects.all()
    serializer_class = ReferralDoctorsSerializer

class PatientHasReferralDoctorsViewSet(viewsets.ModelViewSet):
    queryset = PatientHasReferralDoctors.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PatientHasReferralDoctorsGetSerializer
        elif self.request.method == 'POST' :
            return PatientHasReferralDoctorsPostSerializer
        elif self.request.method == 'PUT':
            return PatientHasReferralDoctorsGetSerializer 

class UsersHasReferralDoctorsViewSet(viewsets.ModelViewSet):
    queryset = UsersHasReferralDoctors.objects.all()
    serializer_class = UsersHasReferralDoctorsSerializer

class UsersHasPatientViewSet(viewsets.ModelViewSet):
    queryset = UsersHasPatient.objects.all()
    serializer_class = UsersHasPatientSerializer

class UsersHasTemplatesViewSet(viewsets.ModelViewSet):
    queryset = UsersHasTemplates.objects.all()
    serializer_class = UsersHasTemplatesSerializer

class PatientReceiveTemplatesViewSet(viewsets.ModelViewSet):
    queryset = PatientReceiveTemplates.objects.all()
    serializer_class = PatientReceiveTemplatesSerializer

class ClinicViewSet(viewsets.ModelViewSet):
    queryset = Clinic.objects.all()
    serializer_class = ClinicSerializer

class VirtualMeetViewSet(viewsets.ModelViewSet):
    queryset = VirtualMeet.objects.all()
    serializer_class = VirtualMeetSerializer

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class TasksViewSet(viewsets.ModelViewSet):
    queryset = Tasks.objects.all()
    serializer_class = TasksSerializer

class RecurrenceViewSet(viewsets.ModelViewSet):
    queryset = Recurrence.objects.all()
    serializer_class = RecurrenceSerializer

class AttachmentReminderViewSet(viewsets.ModelViewSet):
    
    serializer_class = AttachmentReminderSerializer

    def get_queryset(self):
        template_id = self.request.query_params.get("templateID")
        if (template_id):
            queryset = AttachmentReminder.objects.filter(templateID=template_id)
        else:
            queryset = AttachmentReminder.objects.all()
        return queryset

class TemplatesViewSet(viewsets.ModelViewSet):
    queryset = Templates.objects.all()
    serializer_class = TemplatesSerializer

class UsersHasTasksViewSet(viewsets.ModelViewSet):
    queryset = UsersHasTasks.objects.all()
    serializer_class = UsersHasTasksSerializer

class RadiologyTestViewSet(viewsets.ModelViewSet):
    queryset = RadiologyTest.objects.all()
    serializer_class = RadiologyTestSerializer

class RadiologyResultViewSet(viewsets.ModelViewSet):
    queryset = RadiologyResult.objects.all()
    serializer_class = RadiologyResultSerializer

class ReferenceViewSet(viewsets.ModelViewSet):
    queryset = Reference.objects.all()
    serializer_class = ReferenceSerializer

class BillingViewSet(viewsets.ModelViewSet):
    queryset = Billing.objects.all()
    serializer_class = BillingSerializer
    def perform_create(self, serializer):
        # Save the billing entry and get the object
        billing_entry = serializer.save()

        # Generate the invoice_number based on the created billing_id
        billing_entry.invoice_number = f'inv_{billing_entry.billing_id}'
        billing_entry.save()

        # Serialize and return the billing entry with the generated invoice_number
        serializer = self.get_serializer(billing_entry)
        return Response(serializer.data)


def most_prescribed_medications(request, patient_id):
    # Call the model method to retrieve the most prescribed medications
    most_prescribed_meds = PatientHasPrescription.most_prescribed_medications(patient_id)

    # You can process the data as needed and return a JSON response
    data = {
        'most_prescribed_medications': most_prescribed_meds,
    }
    return JsonResponse(data)

class FilesViewSet(viewsets.ModelViewSet):
    queryset = Files.objects.all()
    serializer_class = FilesSerializer

import os

def serve_file(request, file_name):
    # Construct the full path to the file
    file_path = os.path.join(settings.MEDIA_ROOT, 'attachments', file_name)

    if os.path.exists(file_path):
        # Open and serve the file
        with open(file_path, 'rb') as file:
            response = FileResponse(file)
            # Set the Content-Disposition header for inline display
            response['Content-Disposition'] = 'inline; filename="' + os.path.basename(file_path) + '"'
            return response
    else:
        # Handle the case where the file does not exist
        return HttpResponse("File not found", status=404)


def serve_template_attachment(request, file_name):
    # Construct the full path to the file
    file_path = os.path.join(settings.MEDIA_ROOT, 'templates', file_name)

    if os.path.exists(file_path):
        # Open and serve the file
        with open(file_path, 'rb') as file:
            response = FileResponse(file)
            # Set the Content-Disposition header for inline display
            response['Content-Disposition'] = 'inline; filename="' + os.path.basename(file_path) + '"'
            return response
    else:
        # Handle the case where the file does not exist
        return HttpResponse("File not found", status=404)
import json
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def receive_whatsapp_message(request):
    if request.method == 'POST':
        try:
            payload = json.loads(request.body)
            
            # Process the incoming payload as needed
            print("Received forwarded message:", payload)

            # Add your custom logic here to process the forwarded message
            
            return JsonResponse({'status': 'success'})
        except json.JSONDecodeError as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'method not allowed'}, status=405)

    
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime, timezone
import requests  # Import requests module
from django.core.files.base import ContentFile
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def get_token():
    tokens = WhatsAppToken.objects.all()

    if tokens.exists():
        # Assuming you want to get the first token, modify the logic based on your requirements
        first_token = tokens.first()
        return first_token.token
        
    else:
        return None



@csrf_exempt
def whatsapp_webhook(request):
    if request.method == 'GET':
        # Handle verification
        verify_token = "doctor1"  # Replace with your actual verify token
        received_verify_token = request.GET.get("hub.verify_token", "")

        if received_verify_token == verify_token:
            # Respond with the challenge to complete the verification
            challenge = request.GET.get("hub.challenge", "")
            return HttpResponse(challenge, content_type="text/plain")
        else:
            # Respond with an error if tokens do not match
            return HttpResponse("Verification failed", status=403)

    elif request.method == 'POST':
        # Handle message processing
        try:
            payload = json.loads(request.body)
            print("Received", payload)

            # Extract relevant information from the payload
            entry = payload.get('entry', [])
            if entry:
                changes = entry[0].get('changes', [])
                if changes:
                    value = changes[0].get('value', {})
                    contacts = value.get('contacts', [])
                    messages = value.get('messages', [])
                    #message_id = messages[0]['id']
                    # Ensure required data is present
                    if contacts and messages:
                        phone_number = contacts[0].get('wa_id', '')
                        timestamp = messages[0].get('timestamp', 0)
                        received_time = datetime.utcfromtimestamp(int(timestamp)).replace(tzinfo=timezone.utc)

                        # Find patient using phone number and get the ID
                        patient, created = Patient.objects.get_or_create(phone=phone_number)

                        # Find user with role_idrole equal to 1 and get the ID
                       # user = Users.objects.filter(role_idrole=1).first()  # Replace with your actual logic
                        print("mess",messages[0])
                        # Check if the message contains text or media
                        if 'text' in messages[0]:
                            text = messages[0]['text']['body']
                            # Save the message to the database
                            WhatsMessage.objects.create(
                                text=text,
                                #user=user,
                                patient=patient,
                                is_sent=False,
                                received_time=received_time,
                            )
                            channel_layer = get_channel_layer()
                            async_to_sync(channel_layer.group_send)(
                                "whatsapp_group",  # Replace with the actual group name for WhatsApp messages
                                {
                                    "type": "notify.whatsapp_event",
                                    "message": "New WhatsApp message received!",
                                    #"user_id": user.id,  # Include user ID in the WebSocket message
                                    "patient_id": patient.id,  # Include patient ID in the WebSocket message
                                },
                            )
                            print('Text message saved to database')
                            send_acknowledgment(patient.phone, text)
                        elif 'button' in messages[0]:
                            button_payload = messages[0]['button']['payload']
                            # Save the button payload as a text message
                            WhatsMessage.objects.create(
                                text=button_payload,
                                #user=user,
                                patient=patient,
                                is_sent=False,
                                received_time=received_time,
                            )
                            channel_layer = get_channel_layer()
                            async_to_sync(channel_layer.group_send)(
                                "whatsapp_group",  # Replace with the actual group name for WhatsApp messages
                                {
                                    "type": "notify.whatsapp_event",
                                    "message": "New WhatsApp message received!",
                                   # "user_id": user.id,  # Include user ID in the WebSocket message
                                    "patient_id": patient.id,  # Include patient ID in the WebSocket message
                                },
                            )
                            print('Button payload saved as text message to database')
                            send_acknowledgment(patient.phone, 'reply')
                        elif 'location' in messages[0]:
                            location_data = messages[0]['location']
                            latitude = location_data.get('latitude')
                            longitude = location_data.get('longitude')
                            WhatsMessage.objects.create(
                                longitude=longitude,
                                latitude=latitude,
                                #user=user,
                                patient=patient,
                                is_sent=False,
                                received_time=received_time,
                            )
                            channel_layer = get_channel_layer()
                            async_to_sync(channel_layer.group_send)(
                                "whatsapp_group",  # Replace with the actual group name for WhatsApp messages
                                {
                                    "type": "notify.whatsapp_event",
                                    "message": "New WhatsApp message received!",
                                    #"user_id": user.id,  # Include user ID in the WebSocket message
                                    "patient_id": patient.id,  # Include patient ID in the WebSocket message
                                },
                            )
                            print('Location saved to database')
                            send_acknowledgment(patient.phone, 'location')
                        elif 'image' in messages[0]:
                            # Process image media message
                            image_media_id = messages[0]['image']['id']
                            image_url = get_media_url(image_media_id)
                            if image_url:
                                image_data = download_media(image_url)
                                # Save the media information to your database
                                media_obj=Media.objects.create(
                                    media_id=image_media_id,
                                    media_type='image/jpeg',
                                    
                                )
                                
                                media_obj.media_data.save(f"image_{media_obj.id}.jpeg", ContentFile(image_data))
                                media_obj.save()
                                WhatsMessage.objects.create(
                                #user=user,
                                patient=patient,
                                media=media_obj,
                                received_time=received_time,  # Assuming you want to use received_time as sent_timestamp
                                is_sent=False,
                            )
                                print('Image media saved to database')
                                send_acknowledgment(patient.phone, 'image')
                                channel_layer = get_channel_layer()
                                async_to_sync(channel_layer.group_send)(
                                    "whatsapp_group",  # Replace with the actual group name for WhatsApp messages
                                    {
                                        "type": "notify.whatsapp_event",
                                        "message": "New WhatsApp message received!",
                                        #"user_id": user.id,  # Include user ID in the WebSocket message
                                        "patient_id": patient.id,  # Include patient ID in the WebSocket message
                                    },
                                )
                            else:
                                print('Error getting image media URL')
                        elif 'document' in messages[0]:
                            # Process document media message
                            document_media_id = messages[0]['document']['id']
                            document_url = get_media_url(document_media_id)
                            if document_url:
                                document_data = download_media(document_url)
                                # Save the media information to your database
                                media_obj = Media.objects.create(
                                media_id=document_media_id,
                                media_type=messages[0]['document']['mime_type'],
                            )
                                # Determine the file extension based on the MIME type
                                extension = media_obj.media_type.split('/')[-1]
                                media_obj.media_data.save(f"document_{media_obj.id}.{extension}", ContentFile(document_data))
                                media_obj.save()
                                
                                WhatsMessage.objects.create(
                                #user=user,
                                patient=patient,
                                media=media_obj,
                                received_time=received_time,  # Assuming you want to use received_time as sent_timestamp
                                is_sent=False,
                            )
                                channel_layer = get_channel_layer()
                                async_to_sync(channel_layer.group_send)(
                                    "whatsapp_group",  # Replace with the actual group name for WhatsApp messages
                                    {
                                        "type": "notify.whatsapp_event",
                                        "message": "New WhatsApp message received!",
                                        #"user_id": user.id,  # Include user ID in the WebSocket message
                                        "patient_id": patient.id,  # Include patient ID in the WebSocket message
                                    },
                                )
                                print('Document media saved to database')
                                send_acknowledgment(patient.phone, 'document')
                            else:
                                print('Error getting document media URL')
                        elif 'audio' in messages[0]:
                            # Process audio media message
                            audio_media_id = messages[0]['audio']['id']
                            audio_url = get_media_url(audio_media_id)
                            if audio_url:
                                audio_data = download_media(audio_url)
                                # Save the media information to your database
                                media_obj = Media.objects.create(
                                media_id=audio_media_id,
                                media_type=messages[0]['audio']['mime_type'],
                            )
                                # Determine the file extension based on the MIME type
                                extension = media_obj.media_type.split('/')[-1]
                                media_obj.media_data.save(f"audio_{media_obj.id}.{extension}", ContentFile(audio_data))
                                media_obj.save()
                                WhatsMessage.objects.create(
                                #user=user,
                                patient=patient,
                                media=media_obj,
                                received_time=received_time,  # Assuming you want to use received_time as sent_timestamp
                                is_sent=False,
                            )
                                print('Audio media saved to database')
                                send_acknowledgment(patient.phone, 'audio')
                                channel_layer = get_channel_layer()
                                async_to_sync(channel_layer.group_send)(
                                    "whatsapp_group",  # Replace with the actual group name for WhatsApp messages
                                    {
                                        "type": "notify.whatsapp_event",
                                        "message": "New WhatsApp message received!",
                                        #"user_id": user.id,  # Include user ID in the WebSocket message
                                        "patient_id": patient.id,  # Include patient ID in the WebSocket message
                                    },
                                )
                            else:
                                print('Error getting audio media URL')
                        elif 'video' in messages[0]:
                            # Process video media message
                            video_media_id = messages[0]['video']['id']
                            video_url = get_media_url(video_media_id)
                            if video_url:
                                video_data = download_media(video_url)
                                # Save the media information to your database
                                media_obj = Media.objects.create(
                                media_id=video_media_id,
                                media_type='video/mp4',  # Adjust the media type based on actual payload
                            )
                                media_obj.media_data.save(f"video_{media_obj.id}.mp4", ContentFile(video_data))
                                media_obj.save()
                                WhatsMessage.objects.create(
                               # user=user,
                                patient=patient,
                                media=media_obj,
                                received_time=received_time,  # Assuming you want to use received_time as sent_timestamp
                                is_sent=False,
                            )
                                print('Video media saved to database')
                                send_acknowledgment(patient.phone, 'video')
                                channel_layer = get_channel_layer()
                                async_to_sync(channel_layer.group_send)(
                                    "whatsapp_group",  # Replace with the actual group name for WhatsApp messages
                                    {
                                        "type": "notify.whatsapp_event",
                                        "message": "New WhatsApp message received!",
                                        #"user_id": user.id,  # Include user ID in the WebSocket message
                                        "patient_id": patient.id,  # Include patient ID in the WebSocket message
                                    },
                                )
                            else:
                                print('Error getting video media URL')
                        elif 'sticker' in messages[0]:
                            # Process sticker media message
                            sticker_media_id = messages[0]['sticker']['id']
                            sticker_url = get_media_url(sticker_media_id)
                            if sticker_url:
                                sticker_data = download_media(sticker_url)
                                # Save the media information to your database
                                media_obj = Media.objects.create(
                                media_id=sticker_media_id,
                                media_type='image/webp',
                            )
                                media_obj.media_data.save(f"sticker_{media_obj.id}.webp", ContentFile(sticker_data))
                                media_obj.save()
                                WhatsMessage.objects.create(
                                #user=user,
                                patient=patient,
                                media=media_obj,
                                received_time=received_time,  # Assuming you want to use received_time as sent_timestamp
                                is_sent=False,
                            )
                                print('Sticker media saved to database')
                                send_acknowledgment(patient.phone, 'sticker')
                                channel_layer = get_channel_layer()
                                async_to_sync(channel_layer.group_send)(
                                    "whatsapp_group",  # Replace with the actual group name for WhatsApp messages
                                    {
                                        "type": "notify.whatsapp_event",
                                        "message": "New WhatsApp message received!",
                                        #"user_id": user.id,  # Include user ID in the WebSocket message
                                        "patient_id": patient.id,  # Include patient ID in the WebSocket message
                                    },
                                )
                            else:
                                print('Error getting sticker media URL')
                        # Add similar handling for other media types (if any)
                        
                        return JsonResponse({'status': 'success'})

            # If the payload structure is not as expected, return an error response
            return JsonResponse({'status': 'success', 'message': 'Message received but not processed'}, status=200)

        except json.JSONDecodeError as e:
            return JsonResponse({'status': 'error', 'message': 'Error decoding JSON: ' + str(e)}, status=400)

    return JsonResponse({'status': 'method not allowed'}, status=405)

def get_media_url(media_id):
    access_token= get_token()
    # Replace <YOUR_ACCESS_TOKEN> with your actual access token
    #access_token = 'EAAFSezp24bEBO8DFtDmD8Bzevm86reUpawPfGbFZAJqw4y6en3XtEUuu1zDhY8AqhQqvDXLFFfUXSanqzCmyQpOOAjFpZB1wBf0XwRviF6XhGeBHJv9zorVOOWs7LsJVuVdpmYAefuGdo3PHZCdwbDMzR6b5BDxY15ZAtGKHmIlgN6aq685DSrVMZAuO3d9nT0zeXHd8PDeXKB4I2sN0DlDZBrhKT3yVUHDIiOGPXJfzoZD'
    url = f'https://graph.facebook.com/v17.0/{media_id}/'
    headers = {'Authorization': f'Bearer {access_token}'}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        media_url = data.get('url', '')
        return media_url
    except requests.exceptions.RequestException as e:
        # Handle request errors (you can log the error, raise an exception, etc.)
        print(f"Error getting media URL: {e}")
        return None  # Or raise an exception if you want to handle it differently
import base64
def download_media(media_url):
    access_token= get_token()
    #access_token = 'EAAFSezp24bEBO8DFtDmD8Bzevm86reUpawPfGbFZAJqw4y6en3XtEUuu1zDhY8AqhQqvDXLFFfUXSanqzCmyQpOOAjFpZB1wBf0XwRviF6XhGeBHJv9zorVOOWs7LsJVuVdpmYAefuGdo3PHZCdwbDMzR6b5BDxY15ZAtGKHmIlgN6aq685DSrVMZAuO3d9nT0zeXHd8PDeXKB4I2sN0DlDZBrhKT3yVUHDIiOGPXJfzoZD'
    headers = {'Authorization': f'Bearer {access_token}'}

    try:
        response = requests.get(media_url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses

        # Return the response content
        return response.content

    except requests.exceptions.RequestException as e:
        # Handle request errors (you can log the error, raise an exception, etc.)
        print(f"Error downloading media: {e}")
        return None

def mark_message_as_read( message_id):
    access_token= get_token()
    #access_token = 'EAAFSezp24bEBO8DFtDmD8Bzevm86reUpawPfGbFZAJqw4y6en3XtEUuu1zDhY8AqhQqvDXLFFfUXSanqzCmyQpOOAjFpZB1wBf0XwRviF6XhGeBHJv9zorVOOWs7LsJVuVdpmYAefuGdo3PHZCdwbDMzR6b5BDxY15ZAtGKHmIlgN6aq685DSrVMZAuO3d9nT0zeXHd8PDeXKB4I2sN0DlDZBrhKT3yVUHDIiOGPXJfzoZD'
    phone_number_id= '120586281145678'
    url = f'https://graph.facebook.com/v17.0/{phone_number_id}/messages'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    data = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raise an error for bad responses
        print('Message marked as read successfully!')
    except requests.exceptions.RequestException as e:
        # Handle request errors (log the error, raise an exception, etc.)
        print(f"Error marking message as read: {e}")

def send_acknowledgment(recipient_phone, message_type):
    # Construct the acknowledgment message based on the message type
    acknowledgment_text = f"Ack: {message_type}"
    access_token= get_token()
    # Replace this with your logic to send the acknowledgment using the WhatsApp API
    #auth_token = 'EAAFSezp24bEBO8DFtDmD8Bzevm86reUpawPfGbFZAJqw4y6en3XtEUuu1zDhY8AqhQqvDXLFFfUXSanqzCmyQpOOAjFpZB1wBf0XwRviF6XhGeBHJv9zorVOOWs7LsJVuVdpmYAefuGdo3PHZCdwbDMzR6b5BDxY15ZAtGKHmIlgN6aq685DSrVMZAuO3d9nT0zeXHd8PDeXKB4I2sN0DlDZBrhKT3yVUHDIiOGPXJfzoZD'
    phone_number_id= '120586281145678'
    api_url = f'https://graph.facebook.com/v17.0/{phone_number_id}/messages'
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    
    requestBody = {
        'messaging_product': 'whatsapp',
        'recipient_type': 'individual',
        'to': recipient_phone,  # Replace this with the recipient's phone number
        'type': 'text',
        'text': {
            'preview_url': False,
            'body': acknowledgment_text,
        },
    }

    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(requestBody))
        response.raise_for_status()  # Raise an error for bad responses
        print(f"Acknowledgment for {message_type} sent to {recipient_phone}")
    except requests.exceptions.RequestException as e:
        # Handle request errors (log the error, raise an exception, etc.)
        print(f"Error sending acknowledgment: {e}")


class MediaViewSet(viewsets.ModelViewSet):
    queryset = Media.objects.all()
    serializer_class = MediaSerializer

import base64

@api_view(['POST'])
def create_media(request):
    if request.method == 'POST':
        media_id = request.data.get('media_id')
        media_type = request.data.get('media_type')
        binary_data = request.data.get('media_data')

        # If binary_data is a string, convert it to bytes
        if isinstance(binary_data, str):
            binary_data = binary_data.encode('utf-8')

        # Base64 encode binary data
        encoded_data = base64.b64encode(binary_data).decode('utf-8')

        # Save to database
        media = Media.objects.create(
            media_id=media_id,
            media_type=media_type,
            media_data=encoded_data
        )

        return Response({'status': 'success', 'media_id': media.id}, status=status.HTTP_201_CREATED)
    else:
        return Response({'status': 'error', 'message': 'Invalid request method'}, status=status.HTTP_400_BAD_REQUEST)

class WhatsMessageViewSet(viewsets.ModelViewSet):
    queryset = WhatsMessage.objects.all()
    serializer_class = WhatsMessageSerializer

from datetime import timedelta
from django.utils import timezone
from .models import WhatsMessage, PatientReceiveTemplates
import requests

def check_last_received_message(patient, template_date):
    try:
        # Get the patient's last received message
        last_message = WhatsMessage.objects.filter(patient=patient).exclude(received_time__isnull=True).order_by('-received_time').first()
        print("last", last_message)
        if last_message:
            # Calculate the time difference between the last received message and the template date
            time_difference = (template_date - last_message.received_time).total_seconds()

            # Check if the last message was within the last 24 hours
            twenty_four_hours = 24 * 60 * 60  # 24 hours in seconds
            if time_difference < twenty_four_hours:
                return True  # Last received message was within the last 24 hours
            else:
                return False  # Last received message was more than 24 hours ago
        else:
            return False  # No received messages found

    except Exception as e:
        print(f'Error checking last received message: {e}')
        return False


def check_last_received_within_24_hours(patient, template_date):
    try:
        # Get the patient's last received message
        last_message = WhatsMessage.objects.filter(patient=patient).exclude(received_time__isnull=True).order_by('-received_time').first()
        print("lastfuture",last_message)
        if last_message:
            # Calculate the time difference between the last received message and the template date
            time_difference = (template_date - last_message.received_time).total_seconds()

            # Check if the last message was within the last 24 hours
            twenty_four_hours = 24 * 60 * 60  # 24 hours in seconds
            return time_difference < twenty_four_hours
        else:
            return False  # No received messages found

    except Exception as e:
        print(f'Error checking last received message: {e}')
        return False

@csrf_exempt
def scheduled_function(request):
    now = timezone.now()
    print("now", now)
    
    # Calculate the start time for the next 15 minutes
    start_time = now + timedelta(minutes=15)

    # Fetch PatientReceiveTemplates data for the next 15 minutes
    templates = PatientReceiveTemplates.objects.filter(
        status=False,
        date__range=(now, start_time)
    )
    print(f"Fetched {len(templates)} templates for processing at {now}")
    # Create a dummy file to indicate that the scheduled_function is running
    #with open('scheduler_execution.txt', 'w') as f:
       # f.write(f'scheduled_function executed at {now}\n')
        
    for template in templates:
        patient_data = template.patient
        item = template.templates
        if check_last_received_message(patient_data, template.date):
            time_difference = (template.date - now).total_seconds() / 60
            scheduled_time = now + timedelta(minutes=time_difference)
            send_message(item, patient_data, template)
            # Schedule the sending of the message at the calculated time
            #scheduler.add_job(send_message, 'date', run_date=scheduled_time, args=[item, patient_data, template])
            print(f"Message for patient {patient_data.id} with template ID {item.idTemplates} scheduled for {scheduled_time}")
        else:
            print(f"Last received message for patient {patient_data.id} was more than 24 hours ago.")

            # Add 15 minutes to the date attribute if the template is not expired
            if not item.expire:
                if not template.message_updated:
                    # Save the initial date as a string
                    template.initial_date_str = str(template.date)
                    template.message_updated = True  # Set the flag to True to indicate that the message has been updated

                    print(f"updating message")
                else:
                    print(f"Skipping update")
                template.date += timedelta(minutes=15)
                template.save()
                print(f"Added 15 minutes to the template date for patient {patient_data.id}. Updated message body.")
            else:
                print(f"Skipping message scheduling for patient {patient_data.id} as the template is expired.")

    print("Processing completed.")
    future_time_start = now + timedelta(hours=2)
    future_time_end = future_time_start + timedelta(minutes=15)
    future_templates = PatientReceiveTemplates.objects.filter(
        status=False,
        date__range=(future_time_start, future_time_end)
        )
    print("future", future_templates)
        # Send 'reply' template to patients with scheduled messages in the next 2 to 2.15 hours
    for template in future_templates:
        patient_data = template.patient

        # Calculate the time difference between the scheduled time and the current time
        time_difference = (template.date - now).total_seconds() / 60

        # Calculate the time to send the 'reply' template exactly 2 hours before the scheduled time
        scheduled_time = template.date - timedelta(hours=2)
        if not check_last_received_within_24_hours(patient_data, template.date):
            # Schedule the 'reply' template to be sent exactly 2 hours before the scheduled time
            send_reply_template(patient_data)
            #scheduler.add_job(send_reply_template, 'date', run_date=scheduled_time, args=[patient_data])
            print(f"Predefined 'reply' template scheduled for patient {patient_data.id} at {scheduled_time}")
    return HttpResponse("Processing of future templates completed", status=200)


def send_message(item, patient_data, template):
    try:
        auth_token = get_token()
        phone_number_id = '120586281145678'
        api_url_media = f'https://graph.facebook.com/v17.0/{phone_number_id}/media'
        api_url = f'https://graph.facebook.com/v17.0/120586281145678/messages'
        print(f"Sending message for patient {patient_data.id} with template ID {item.idTemplates}")
        recipient_phone = patient_data.phone
        print("item", item.body)
        if not item.body:
            print("t")
            attachment_response = requests.get('https://saugo.azurewebsites.net/attachment-reminders/', params={'templateID': item.idTemplates})
            print("res", attachment_response)
            attachment_data = attachment_response.json()
  
            if attachment_data and len(attachment_data) > 0:
                print("data")
                attachment = attachment_data[0]
                file_response = requests.get(attachment['attachment_file'], stream=True)
                file = file_response.content
                print("atta")
                supported_types = [
                    'audio/aac', 'audio/mp4', 'audio/mpeg', 'audio/amr', 'audio/ogg',
                    'audio/ogg; codecs:opus', 'text/plain', 'application/pdf',
                    'application/vnd.ms-powerpoint', 'application/msword', 'application/vnd.ms-excel',
                    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    'image/jpeg', 'image/png', 'video/mp4', 'video/3gp', 'image/webp'
                ]
  
                if attachment['type'] in supported_types:
                    print("type")
                    payload = {
                        'type': attachment['type'],
                        'messaging_product': 'whatsapp',
                    }

                    files = {
                        'file': (attachment['name'], file, attachment['type']),
                    }

                    headers = {
                        'Authorization': f'Bearer {auth_token}',
                    }
                    upload_response = requests.post(api_url_media, data=payload, files=files, headers=headers)

                    upload_result = upload_response.json()
                    media_type = get_media_content(attachment['type'])
                    print("media", media_type)
                    print("upload", upload_response)
                    if upload_result.get('id') and media_type:
                        print("if")
                        request_body = {
                            'messaging_product': 'whatsapp',
                            'recipient_type': 'individual',
                            'to': recipient_phone,
                            'type': media_type,
                            media_type: {'id': upload_result['id']}
                        }
  
                        response = requests.post(api_url, json=request_body, headers={'Authorization': f'Bearer {auth_token}', 'Content-Type': 'application/json'})
                        print(f'Media message sent: {response.json()}')
                        template.status = True
                        template.save()
                        media_instance = Media.objects.create(
                        media_id=upload_result['id'],
                        media_type=attachment['type'],
                        
                    )
                        extension = attachment['type'].split('/')[-1]
                        media_instance.media_data.save(f"media_{media_instance.id}.{extension}", ContentFile(file))
                        media_instance.save()
                        # Save message information in the WhatsMessage model
                        whats_message_instance = WhatsMessage.objects.create(

                            patient=patient_data,
                            media=media_instance,
                            sent_timestamp=timezone.now(),  
                            is_sent=True,

                        )
                        # Check conditions for sending additional text message
                        if template.message_updated and template.initial_date_str:
                            additional_message = f"This message should have been sent at the original scheduled date: {template.initial_date_str} (GMT)"
                            send_additional_text_message(additional_message, recipient_phone, auth_token, api_url)
        else:
            # Check conditions for appending sentence to text message
            bodymessage = item.body
            if template.message_updated and template.initial_date_str:
                additional_sentence = f"This message should have been sent at the original scheduled date: {template.initial_date_str} (GMT)"
                bodymessage += f"\n\n{additional_sentence}"
                request_body = {
                    'messaging_product': 'whatsapp',
                    'recipient_type': 'individual',
                    'to': recipient_phone,
                    'type': 'text',
                    'text': {'preview_url': False, 'body': bodymessage}
                }
            else:
                
                request_body = {
                    'messaging_product': 'whatsapp',
                    'recipient_type': 'individual',
                    'to': recipient_phone,
                    'type': 'text',
                    'text': {'preview_url': False, 'body': bodymessage}
                }
            response = requests.post(api_url, json=request_body, headers={'Authorization': f'Bearer {auth_token}', 'Content-Type': 'application/json'})
            print(f'Text message sent: {response.json()}')
            template.status = True
            template.save()
            whats_message_instance = WhatsMessage.objects.create(
                            text=bodymessage,
                            patient=patient_data,
                            sent_timestamp=timezone.now(),  
                            is_sent=True,
                        )
            print("saved to database")
    except Exception as e:
        print(f'Error sending WhatsApp messages: {e}')
        raise e

def get_media_content(media_type):
    supported_media_types = {
        'audio': ['audio/aac', 'audio/mp4', 'audio/mpeg', 'audio/amr', 'audio/ogg', 'audio/ogg; codecs:opus'],
        'document': [
            'text/plain', 'application/pdf', 'application/vnd.ms-powerpoint',
            'application/msword', 'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ],
        'image': ['image/jpeg', 'image/png', 'image/webp'],
        'video': ['video/mp4', 'video/3gp']
    }
  
    for content_type, types in supported_media_types.items():
        if media_type in types:
            return content_type
  
    return None  # Unsupported media type

def send_reply_template(patient_data):
    try:
       
        auth_token = get_token()
        recipient_phone = patient_data.phone
        apiUrl = 'https://graph.facebook.com/v17.0/120586281145678/messages'

        requestBody = {
            'messaging_product': 'whatsapp',
            'to': recipient_phone,
            'type': 'template',
            'template': {
                'name': 'reply',
                'language': {'code': 'en'}
            },
        }

        response = requests.post(apiUrl, json=requestBody, headers={'Authorization': f'Bearer {auth_token}', 'Content-Type': 'application/json'})
        print(f"Predefined 'reply' template sent: {response.json()}")

    except Exception as e:
        print(f'Error sending predefined "reply" template: {e}')

def send_additional_text_message(additional_message, recipient_phone, auth_token, api_url):
    try:
        request_body = {
            'messaging_product': 'whatsapp',
            'recipient_type': 'individual',
            'to': recipient_phone,
            'type': 'text',
            'text': {'preview_url': False, 'body': additional_message}
        }

        response = requests.post(api_url, json=request_body, headers={'Authorization': f'Bearer {auth_token}', 'Content-Type': 'application/json'})
        print(f'Additional text message sent: {response.json()}')
    except Exception as e:
        print(f'Error sending additional text message: {e}')
        raise e

import subprocess
from django.http import HttpResponse

def trigger_scheduler(request):
    try:
        # Replace 'python3' with the appropriate command for your environment (e.g., 'python', 'python3.8', etc.)
        command = 'python ../scheduler.py'  # Replace with your actual path
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()

        if error:
            return HttpResponse(f'Error running scheduler: {error}', status=500)
        else:
            return HttpResponse(f'Scheduler triggered successfully\nOutput: {output.decode("utf-8")}', status=200)
    except Exception as e:
        return HttpResponse(f'Error triggering scheduler: {str(e)}', status=500)
