from django.shortcuts import render
from django.http.response import JsonResponse
from .models import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import *
from django.http import Http404
from rest_framework import generics,mixins,viewsets,filters
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.authentication import TokenAuthentication
from django.db.models.signals import post_save
from django.dispatch import receiver 
from rest_framework.authtoken.models import Token
from django.conf import settings
from .permissions import *

# Create your views here.

#1 without Rest and no model
def no_rest_no_model(request):
    guests=[
        {
            'id':1,
            'Name':'omar',
            'mobile':22214324
        },
        {
            'id':2,
            'Name':'yassin',
            'mobile':12432576
        }
        
    ]
    
    return JsonResponse(guests,safe=False)

#2 model data default without rest
def no_rest_from_model(request):
    data=Guest.objects.all()
    
    response={
        'guests':list(data.values('name','mobile'))
    }
    
    return JsonResponse(response)
    
#3 function based view(FVB) with api_view (rest)
@api_view(['GET','POST'])
def FBV_List(request):
    #GET
    if request.method == "GET":
        guests=Guest.objects.all()
        serializer=GuestSerializer(guests,many=True)
        return Response(serializer.data)
    #POST
    if request.method == "POST":
        serializer=GuestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.data,status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET','PUT','DELETE'])
def FBV_pk(request,pk):
    try:
        guest=Guest.objects.get(pk=pk)
    except Guest.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND) 
    #GET
    if request.method == "GET":
        serializer=GuestSerializer(guest)
        return Response(serializer.data)
    #PUT
    if request.method == "PUT":
        serializer=GuestSerializer(guest,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
     #DELETE
    if request.method == "DELETE":
        guest.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


#CBV class based views
#4.1 List and Create == GET and POST
class CBV_List(APIView):
    def get(self,request):
        guests=Guest.objects.all()
        serializer=GuestSerializer(guests,many=True)
        return Response(serializer.data)
    
    def post(self,request):
        serializer=GuestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
#4.2 GET PUT DELETE class based view --pk
class CBV_pk(APIView):
    
    def get_object(self,pk):
        try:
            return Guest.objects.get(pk=pk)
        except Guest.DoesNotExist:
            raise Http404
        
    def get(self,request,pk):
      guest=self.get_object(pk)
      serializer=GuestSerializer(guest)
      return Response(serializer.data)  

    
    def put(self,request,pk):
        guest=self.get_object(pk)
        serializer=GuestSerializer(guest,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request,pk):
        guest=self.get_object(pk)
        guest.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
#5 mixins
#5.1 mixins list
class mixins_list(mixins.ListModelMixin,mixins.CreateModelMixin,generics.GenericAPIView):
    queryset=Guest.objects.all()
    serializer_class=GuestSerializer
    
    def get(self,request):
        return self.list(request)
    
    def  post(self,request):
        return self.create(request)
    
#5.3 get put delete
class mixins_pk(mixins.RetrieveModelMixin,mixins.UpdateModelMixin,mixins.DestroyModelMixin,generics.GenericAPIView):
    queryset=Guest.objects.all()
    serializer_class=GuestSerializer
    
    def get(self,request,pk):
        return self.retrieve(request)
    
    def  put(self,request,pk):
        return self.update(request)
    
    def  delete(self,request,pk):
        return self.destroy(request)
    
    
#Generics
#6.1 get(list) post(create)
class Generics_list(generics.ListCreateAPIView):
    queryset=Guest.objects.all()
    serializer_class=GuestSerializer
    authentication_classes=[TokenAuthentication]

#6.2 put update delete -- pk
class Generics_pk(generics.RetrieveUpdateDestroyAPIView):
    queryset=Guest.objects.all()
    serializer_class=GuestSerializer
    authentication_classes=[TokenAuthentication]
    
    
#7 viewsets
#guests
class viewsets_guests(viewsets.ModelViewSet):
    queryset=Guest.objects.all()
    serializer_class=GuestSerializer
    
#movies  
class viewsets_movie(viewsets.ModelViewSet):
    queryset=Movie.objects.all()
    serializer_class=MovieSerializer
    
    filter_backends = [filters.SearchFilter]
    search_fields=['movie']
    
#Reservations 
class viewsets_reservation(viewsets.ModelViewSet):
    queryset=Reservation.objects.all()
    serializer_class=ReservationSerializer    



#8 find_movie (fbv)
@api_view(['GET'])
def find_movie(request):
    movies=Movie.objects.filter(
        hall=request.data['hall'],
        movie=request.data['movie']
    )
    serializer=MovieSerializer(movies)
    if serializer.is_valid():
        serializer.save()
        return Response(request.data)
    
    
#9 create and reservation
@api_view(['POST'])
def new_reservation(request):
    guest=Guest()
    guest.name=request.data['name']
    guest.mobile=request.data['mobile']
    guest.save()
    
    movie=Movie()
    movie.hall=request.data['hall']
    movie.movie=request.data['movie']
    movie.date=request.data['date']
    movie.save()
    
    reservation=Reservation()
    reservation.movie=movie
    reservation.guest=guest
    reservation.save()
    

#signal for make token for new users
@receiver(post_save,sender=settings.AUTH_USER_MODEL)
def create_token(sender,instance,created,**kwargs):
    if created:
        Token.objects.create(user=instance)


# post view 
class post_pk(generics.RetrieveUpdateDestroyAPIView):
    queryset=Post.objects.all()
    serializer_class=PostSerializer
    permission_classes =[IsAuthorOrSuperUser]