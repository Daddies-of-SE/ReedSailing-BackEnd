#### 1,ModelSerializer

- 目的: 可以使用ModelSerializer根据模型类生成字段

- 作用:

  - 1, 可以参考模型类自动生成字段, 还可以自己编写字段
  - 2, 提供了create方法,update方法

- 操作流程:

  - 1, 定义模型类序列化器

    - ```python
      from rest_framework import serializers
      from booktest.models import BookInfo
      
      #1,定义书籍模型类序列化器
      class BookModelSerializer(serializers.ModelSerializer):
      
          # mobile = serializers.CharField(max_length=11,min_length=11,label="手机号",write_only=True)
      
          class Meta:
              model = BookInfo #参考模型类生成字段
              fields = "__all__" #生成所有字段
      ```

  - 2, 测试结果

    - ```python
      """==============1, 使用模型类序列化器, 测试序列化 ========================"""""
      """
      1, 模型类中添加mobile字段
      2, 删除序列化器中的mobile
      3, 动态添加一mobile属性
      4, 将mobile字段设置为write_only(只写,只进行反序列化)
      """
      from booktest.models import BookInfo
      from booktest.serializer import BookModelSerializer
      
      #1,获取模型类对象
      book = BookInfo.objects.get(id=1)
      # book.mobile = "13838389438"
      
      #2,创建序列化器对象
      serializer = BookModelSerializer(instance=book)
      
      #3,输出结果
      serializer.data
      
      """==============2, 使用模型类序列化器, 测试反序列化, 入库操作========================"""""
      from booktest.serializer import BookModelSerializer
      
      #1,准备字典数据
      book_dict = {
          "btitle":"鹿鼎记1",
          "bpub_date":"1999-01-01",
          "bread":10,
          "bcomment":5
      }
      
      #2,序列化器对象创建
      serializer = BookModelSerializer(data=book_dict)
      
      #3,校验,入库
      serializer.is_valid(raise_exception=True)
      serializer.save()
      
      """==============3, 使用模型类序列化器, 测试反序列化, 更新操作========================"""""
      from booktest.serializer import BookModelSerializer
      from booktest.models import BookInfo
      
      #1,准备字典数据, 书籍对象
      book = BookInfo.objects.get(id=9)
      book_dict = {
          "btitle":"鹿鼎记2",
          "bpub_date":"1999-01-01",
          "bread":100,
          "bcomment":5
      }
      
      #2,序列化器对象创建
      serializer = BookModelSerializer(instance=book,data=book_dict)
      
      #3,校验,入库
      serializer.is_valid(raise_exception=True)
      serializer.save()
      
      ```

#### 2, fields

- 目的: 可以使用fields生成指定的字段

- 操作流程:

  - 1, 序列化器

  - ```python
    #1,定义书籍模型类序列化器
    class BookModelSerializer(serializers.ModelSerializer):
    
        mobile = serializers.CharField(max_length=11,min_length=11,label="手机号",write_only=True)
    
        class Meta:
            model = BookInfo #参考模型类生成字段
            # fields = "__all__" #生成所有字段
    
            #1,生成指定的字段
            fields = ["id","btitle","mobile"]
    ```

  - fields: 生成指定的字段

  - 注意点:

    - 进入到ModelSerializer父类, 1063行源码中存在

#### 3,read_only_fields

- 目的:可以使用read_only_fields设置只读字段

- 操作流程:

  - 1,序列化器

  - ```python
    #1,定义书籍模型类序列化器
    class BookModelSerializer(serializers.ModelSerializer):
    
        ....
    
        class Meta:
            ....
            
            #2,设置只读字段
            read_only_fields = ["btitle","bpub_date"]
    ```

#### 4,extra_kwargs

- 目的: 可以使用extra_kwargs, 给生成的字段,添加选项约束

- 操作流程:

  - 1, 序列化器

    - ```python
      #1,定义书籍模型类序列化器
      class BookModelSerializer(serializers.ModelSerializer):
      
          ...
      
          class Meta:
              ...
              
              #3,给生成的字段添加额外约束
              extra_kwargs = {
                  "bread":{
                      "max_value":999999,
                      "min_value":0
                  },
                  "bcomment": {
                      "max_value": 888888,
                      "min_value": 0
                  }
              }
      ```

#### 5,APIView之request

- 目的: 知道APIView的特点, 并且可以通过request获取参数

- 特点:

  - 1, 继承自View
  - 2, 提供了自己的request对象
    - get参数: request.query_params
    - post参数: request.data
  - 3, 提供了自己的response对象
  - 4, 并且提供了认证, 权限, 限流等功能

- 操作流程:

  - 1, 类视图

    - ```python
      #1,定义类,集成APIView
      class BookAPIView(APIView):
      
          def get(self,request):
              """
              View获取数据方式:
                  GET:
                      request.GET
                  POST:
                      request.POST
                      request.body
      
              APIView获取数据方式
                  GET:
                      reqeust.query_params
                  POST:
                      request.data
      
              :param request:
              :return:
              """
              #1,获取APIVIew中的get请求参数
              # print(request.query_params)
      
              return http.HttpResponse("get")
      
          def post(self,request):
      
              # 2,获取APIView中的post的参数
              print(request.data)
      
              return http.HttpResponse("post")
      ```

#### 6,APIView之Response

- 目的: 可以使用response响应各种数据和状态

- 好处:

  - 1,使用一个类, 就可以替代以前View中的各种类型的Response(HttpResponse,JsonResponse….)
  - 2, 可以配合状态码status使用

- 操作流程:

  - 1,类视图

    - ```python
      from rest_framework.views import APIView
      from django import http
      from rest_framework.response import Response
      from rest_framework import status
      
      #1,定义类,集成APIView
      class BookAPIView(APIView):
      
          def get(self,request):
              ...
      
      			return Response([{"name":"zhangsan"},	{"age":13}],status=status.HTTP_404_NOT_FOUND)
      ```

#### 7,APIView实现列表视图

- 目的: 可以使用序列化器和APIView对列表视图进行改写

- 操作流程:

  - 1, 子路由

    - ```python
      from django.conf.urls import url
      from . import views
      
      urlpatterns = [
          # url(r'^books/$',views.BookAPIView.as_view()),
          url(r'^books/$',views.BookListAPIView.as_view())
      ]
      ```

  - 2, 类视图

    - ```python
      #2,序列化器和APIView实现列表视图
      class BookListAPIView(APIView):
      
          def get(self,request):
              #1,查询所有的书籍
              books = BookInfo.objects.all()
      
              #2,将对象列表转成字典列表
              serializr = BookInfoModelSerializer(instance=books,many=True)
      
              #3,返回响应
              return Response(serializr.data)
      
      
          def post(self,request):
              #1,获取参数
              data_dict = request.data
      
              #2,创建序列化器
              serializer = BookInfoModelSerializer(data=data_dict)
      
              #3,校验,入库
              serializer.is_valid(raise_exception=True)
              serializer.save()
      
              #4,返回响应
              return Response(serializer.data,status=status.HTTP_201_CREATED)
      ```

  - 3, 序列化器

    - ```python
      from rest_framework import serializers
      from booktest.models import BookInfo
      
      #1,定义书籍模型类序列化器
      class BookInfoModelSerializer(serializers.ModelSerializer):
          class Meta:
              model = BookInfo
              fields = "__all__"
      ```

#### 8,APIView实现详情视图

- 目的: 可以使用模型类序列化器和APVIew改写详情视图

- 操作流程:

  - 1, 子路由

    - ```python
      from django.conf.urls import url
      from . import views
      
      urlpatterns = [
          ...
        
          url(r'^books/(?P<book_id>\d+)/$',views.BookDetailAPIView.as_view()),
      ]
      ```

  - 2, 类视图

    - ```python
      #3,序列化器和APIView实现详情视图
      class BookDetailAPIView(APIView):
          def get(self,request,book_id):
      
              #1,获取书籍
              book = BookInfo.objects.get(id=book_id)
      
              #2,创建序列化器对象
              serializer = BookInfoModelSerializer(instance=book)
      
              #4,返回响应
              return Response(serializer.data,status=status.HTTP_200_OK)
      
          def put(self,request,book_id):
      
              #1,获取数据,获取对象
              data_dict = request.data
              book = BookInfo.objects.get(id=book_id)
      
              #2,创建序列化器对象
              serializer = BookInfoModelSerializer(instance=book,data=data_dict)
      
              #3,校验,入库
              serializer.is_valid(raise_exception=True)
              serializer.save()
      
              #4,返回响应
              return Response(serializer.data,status=status.HTTP_201_CREATED)
      
          def delete(self,request,book_id):
      
              #1,删除书籍
              BookInfo.objects.get(id=book_id).delete()
      
              #2,返回响应
              return Response(status=status.HTTP_204_NO_CONTENT)
      ```

#### 9,二级视图,实现列表视图

- 目的: 可以通过GenericAPIView改写列表视图

- 操作流程:

  - 1,子路由

    - ```python
      url(r'^generic_apiview_books/$',views.BookListGenericAPIView.as_view()),
      ```

  - 2, 类视图

    - ```python
      #4,二级视图GenericAPIView特点
      """
      特点: 
      1, GenericAPIView,继承自APIView类，为列表视图, 和详情视图,添加了常用的行为和属性。
          行为(方法)
              get_queryset
              get_serializer
          
          属性
              queryset
              serializer_class
      
      2, 可以和一个或多个mixin类配合使用。
      """
      
      #5,使用二级视图GenericAPIView实现, 列表视图
      class BookListGenericAPIView(GenericAPIView):
      
          #1,提供公共的属性
          queryset = BookInfo.objects.all()
          serializer_class = BookInfoModelSerializer
      
      
          def get(self,request):
              #1,查询所有的书籍
              # books = self.queryset
              books = self.get_queryset()
      
              #2,将对象列表转成字典列表
              # serializr = BookInfoModelSerializer(instance=books,many=True)
              # serializr = self.serializer_class(instance=books,many=True)
              # serializr = self.get_serializer_class()(instance=books,many=True)
              serializr = self.get_serializer(instance=books,many=True)
      
              #3,返回响应
              return Response(serializr.data)
      
      
          def post(self,request):
              #1,获取参数
              data_dict = request.data
      
              #2,创建序列化器
              # serializer = BookInfoModelSerializer(data=data_dict)
              serializer = self.get_serializer(data=data_dict)
      
              #3,校验,入库
              serializer.is_valid(raise_exception=True)
              serializer.save()
      
              #4,返回响应
              return Response(serializer.data,status=status.HTTP_201_CREATED)
      ```

#### 10,二级视图,实现详情视图

- 目的: 可以使用GenericAPIView改写详情视图

- 操作流程:

  - 1, 子路由

    - ```python
      url(r'^generic_apiview_books/(?P<pk>\d+)/$',views.BookDetailGenericAPIView.as_view()),
      ```

  - 2, 类视图

    - ```python
      #6,使用二级视图GenericAPIView实现, 详情视图
      class BookDetailGenericAPIView(GenericAPIView):
      
          #1,提供通用属性
          queryset = BookInfo.objects.all()
          serializer_class = BookInfoModelSerializer
      
          def get(self,request,pk):
      
              #1,获取书籍
              # book = BookInfo.objects.get(id=book_id)
              book = self.get_object() #根据book_id到queryset中取出书籍对象
      
              #2,创建序列化器对象
              serializer = self.get_serializer(instance=book)
      
              #4,返回响应
              return Response(serializer.data,status=status.HTTP_200_OK)
      
          def put(self,request,pk):
      
              #1,获取数据,获取对象
              data_dict = request.data
              book = self.get_object()
      
              #2,创建序列化器对象
              serializer = self.get_serializer(instance=book,data=data_dict)
      
              #3,校验,入库
              serializer.is_valid(raise_exception=True)
              serializer.save()
      
              #4,返回响应
              return Response(serializer.data,status=status.HTTP_201_CREATED)
      
          def delete(self,request,pk):
      
              #1,删除书籍
              self.get_object().delete()
      
              #2,返回响应
              return Response(status=status.HTTP_204_NO_CONTENT)
      ```

#### 11,get_object方法

- 目的: 理解get_object如何根据pk在queryset获取的单个对象

- 二级视图GenericAPIView属性方法总结

  - ```python
    """
    特点: 
    1, GenericAPIView,继承自APIView类，为列表视图, 和详情视图,添加了常用的行为和属性。
        行为(方法)
            get_queryset:  获取queryset的数据集
            get_serializer: 获取serializer_class序列化器对象
            get_object:    根据lookup_field获取单个对象
        
        属性
            queryset:   通用的数据集
            serializer_class: 通用的序列化器
            lookup_field:   默认是pk,可以手动修改id
    
    2, 可以和一个或多个mixin类配合使用。
    """
    ```

- 操作流程:

  - 1, 类视图

    - ````python
      class BookDetailGenericAPIView(GenericAPIView):
      
          #1,提供通用属性
          ...
          lookup_field = "id"
      
          def get(self,request,id):
      
              #1,获取书籍
              book = self.get_object() #根据id到queryset中取出书籍对象
      
              ...
      
          def put(self,request,id):
      
              #1,获取数据,获取对象
      				...
              book = self.get_object()
      
              ...
      
          def delete(self,request,id):
      
              #1,删除书籍
              self.get_object().delete()
      
              ...
      
      ````

#### 12,MiXin

- 目的: 知道mixin的作用, 常见的mixin类

- 操作流程:

  - ```python
    """
    Mixin,特点: 
    1, mixin类提供用于提供基本视图行为(列表视图, 详情视图)的操作
    2, 配合二级视图GenericAPIView使用的
    
    类名称                 提供方法        功能
    ListModelMixin        list          查询所有的数据
    CreateModelMixin      create        创建单个对象
    RetrieveModelMixin    retrieve      获取单个对象
    UpdateModelMixin      update        更新单个对象
    DestroyModelMixin     destroy       删除单个对象
    
    """
    ```

#### 13,二级视图,MiXin配合使用

- 目的: 可以使用mixin和二级视图GenericAPIView对列表视图和详情视图做改写

- 操作流程:

  - 1, 子路由

    - ```python
          url(r'^mixin_generic_apiview_books/$',
              views.BookListMixinGenericAPIView.as_view()),
        
          url(r'^mixin_generic_apiview_books/(?P<book_id>\d+)/$',
              views.BookDetailMixinGenericAPIView.as_view()),
      ```

    - 

  - 2,类视图

    - ```python
      from rest_framework.mixins import ListModelMixin,CreateModelMixin,RetrieveModelMixin,UpdateModelMixin,DestroyModelMixin
      #8,mixin和二级视图GenericAPIView, 实现列表视图, 详情视图
      class BookListMixinGenericAPIView(GenericAPIView,ListModelMixin,CreateModelMixin):
      
          #1,提供公共的属性
          queryset = BookInfo.objects.all()
          serializer_class = BookInfoModelSerializer
      
          def get(self,request):
              return self.list(request)
      
      
          def post(self,request):
              return self.create(request)
      
      
      class BookDetailMixinGenericAPIView(GenericAPIView,RetrieveModelMixin,UpdateModelMixin,DestroyModelMixin):
      
          #1,提供通用属性
          queryset = BookInfo.objects.all()
          serializer_class = BookInfoModelSerializer
          # lookup_field = "id"
          lookup_url_kwarg = "book_id"
      
          def get(self,request,book_id):
              return self.retrieve(request)
      
          def put(self,request,book_id):
              return self.update(request)
      
          def delete(self,request,book_id):
              return self.destroy(request)
      ```

#### 14,三级视图

- 目的: 知道三级视图的作用, 以及常见的三级视图

- 操作流程:

  - ```python
    """
    特点:
    如果没有大量自定义的行为, 可以使用通用视图(三级视图)解决
    
    常见的三级视图:
    类名称                 父类              提供方法        作用
    CreateAPIView       GenericAPIView，   post           创建单个对象
                        CreateModelMixin
                        
    ListAPIView         GenericAPIView,    get            查询所有的数据
                        ListModelMixin
    
    RetrieveAPIView     GenericAPIView,    get            获取单个对象
                        RetrieveModelMixin 
                        
    DestroyAPIView      GenericAPIView,    delete         删除单个对象
                        DestroyModelMixin
                        
    UpdateAPIView       GenericAPIView,    put            更新单个对象
                        UpdateModelMixin             
    
    
    """
    ```

#### 15,三级视图,实现列表,详情视图

- 目的: 可以使用三级视图实现列表视图,详情视图功能

- 操作流程:

  - 1,子路由

    - ```python
          url(r'^third_view/$',views.BookListThirdView.as_view()),
          url(r'^third_view/(?P<pk>\d+)/$',
              views.BookDetailThirdView.as_view()),
      ```

  - 2,类视图

    - ```python
      #10,三级视图,实现列表,详情视图
      from rest_framework.generics import ListAPIView,CreateAPIView
      class BookListThirdView(ListAPIView,CreateAPIView):
      
          #1,提供公共的属性
          queryset = BookInfo.objects.all()
          serializer_class = BookInfoModelSerializer
      
      from rest_framework.generics import RetrieveAPIView,UpdateAPIView,DestroyAPIView
      class BookDetailThirdView(RetrieveAPIView,UpdateAPIView,DestroyAPIView):
      
          #1,提供通用属性
          queryset = BookInfo.objects.all()
          serializer_class = BookInfoModelSerializer
      ```

#### 16,视图集

- 目的: 知道视图集的作用, 以及常见的视图集

- 操作流程:

  - ```python
    """
    视图集
    特点:
        1,可以将一组相关的操作, 放在一个类中进行完成
        2,不提供get,post方法, 使用retrieve, create方法来替代
        3,可以将标准的请求方式(get,post,put,delete), 和mixin中的方法做映射
        
    常见的视图集:
    类名称                 父类              作用
    ViewSet               APIView          可以做路由映射
                          ViewSetMixin
                          
    GenericViewSet        GenericAPIView   可以做路由映射,可以使用三个属性,三个方法
                          ViewSetMixin
                                 
    ModelViewSet          GenericAPIView   所有的增删改查功能,可以使用三个属性,三个方法
                          5个mixin类
    
    ReadOnlyModelViewSet  GenericAPIView   获取单个,所有数据,可以使用三个属性,三个方法
                          RetrieveModelMixin
                          ListModelMixin
    
    """
    ```

#### 17,ViewSet

- 目的: 可以使用ViewSet实现获取所有,单个数据

- 操作流程:

  - 1,子路由

    - ```python
          url(r'^viewset/$',views.BooksViewSet.as_view({'get': 'list'})),
          url(r'^viewset/(?P<pk>\d+)/$',views.BooksViewSet.as_view({'get': 'retrieve'}))
      ```

  - 2,类视图

    - ```python
      #12, 使用viewset实现获取所有和单个
      from django.shortcuts import get_object_or_404
      from booktest.serializer import BookInfoModelSerializer
      from rest_framework import viewsets
      
      class BooksViewSet(viewsets.ViewSet):
          """
          A simple ViewSet for listing or retrieving books.
          """
          def list(self, request):
              queryset = BookInfo.objects.all()
              serializer = BookInfoModelSerializer(instance=queryset, many=True)
              return Response(serializer.data)
      
          def retrieve(self, request, pk=None):
              queryset = BookInfo.objects.all()
              book = get_object_or_404(queryset, pk=pk)
              serializer = BookInfoModelSerializer(instance=book)
              return Response(serializer.data)
      ```

#### 18,ReadOnlyModelViewSet

- 目的: 可以使用ReadOnlyModelViewSet获取所有, 和单个数据

- 操作流程:

  - 1, 子路由

    - ```python
          url(r'^readonly_viewset/$', views.BooksReadOnlyModelViewSet.as_view({'get': 'list'})),
        
          url(r'^readonly_viewset/(?P<pk>\d+)/$', views.BooksReadOnlyModelViewSet.as_view({'get': 'retrieve'})),
      ```

  - 2, 类视图

    - ```python
      #13,使用ReadOnlyModelViewSet实现获取单个和所有
      from rest_framework.viewsets import ReadOnlyModelViewSet
      class BooksReadOnlyModelViewSet(ReadOnlyModelViewSet):
          queryset = BookInfo.objects.all()
          serializer_class = BookInfoModelSerializer
      ```

#### 19,ModelViewSet

- 目的: 使用ModelViewSet实现列表视图,详情视图功能

- 操作流程:

  - 1, 子路由

    - ```python
          url(r'^model_viewset/$', 
              views.BookModelViewSet.as_view({'get': 'list',"post":"create"})),
        
          url(r'^model_viewset/(?P<pk>\d+)/$', 
              views.BookModelViewSet.as_view({'get': 'retrieve','put':'update','delete':'destroy'})),
      ```

  - 2, 类视图

    - ```python
      #14,ModelViewSet实现列表视图,详情视图功能
      from rest_framework.viewsets import ModelViewSet
      class BookModelViewSet(ModelViewSet):
          queryset = BookInfo.objects.all()
          serializer_class = BookInfoModelSerializer
      ```