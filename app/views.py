from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.views.generic import ListView
from django.db import transaction, IntegrityError
from django.http import JsonResponse, HttpResponseForbidden
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from datetime import date, datetime
import json
from itertools import islice

from .models import (
    Usuario,
    Cidade,
    Ocupacao,
    Evento,
    Agendamento,
    Relatorio,
    ResultadoCalculadora,
    Post,
    Comment
)

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

@login_required
@csrf_exempt
def salvar_agendamento(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            data_agend = data.get("data")
            hora = data.get("hora")
            titulo = data.get("titulo")  # Opcional: se quiser armazenar, pode criar um campo "titulo" no modelo

            usuario = request.user.usuario  # Pegando o perfil Usuario

            # Usando ocupacao e cidade do perfil do usuário
            ocupacao = usuario.ocupacao
            cidade = usuario.cidade

            Agendamento.objects.create(
                usuario=usuario,
                ocupacao=ocupacao,
                cidade=cidade,
                data_agend=data_agend,
                horario=hora
            )

            return JsonResponse({"status": "ok"})

        except Exception as e:
            return JsonResponse({"status": "erro", "mensagem": str(e)})


@csrf_exempt
@require_POST
def add_comment(request):
    try:
        data = json.loads(request.body)
        text = data.get('text', '').strip()
        author_name = data.get('author_name', '').strip()
        post_id = data.get('post_id', 1)
        
        if not text:
            return JsonResponse({'success': False, 'error': 'O comentário não pode estar vazio'})
        
        post = get_object_or_404(Post, id=post_id)
        
        comment = Comment(
            post=post,
            text=text,
            created_at=timezone.now(),
            approved=True
        )
        
        if request.user.is_authenticated:
            comment.author = request.user
            comment.author_name = request.user.username
        elif author_name:
            comment.author_name = author_name
        else:
            comment.author_name = "Anônimo"
        
        comment.save()
        
        return JsonResponse({
            'success': True,
            'comment': {
                'id': comment.id,
                'author_name': comment.author_name,
                'text': comment.text,
                'created_at': comment.created_at.strftime('%d/%m/%Y %H:%M'),
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

class IndexView(View):
    def get(self, request):
        post, created = Post.objects.get_or_create(
            id=1,
            defaults={
                'title': 'Página Inicial - Comentários',
                'content': 'Comentários da comunidade sobre a plataforma Inner Pulse'
            }
        )
        comments = post.comments.filter(approved=True)
        
        comments_list = list(comments)
        slides = []
        for i in range(0, len(comments_list), 2):
            slides.append(comments_list[i:i+2])
        
        slide_indices = range(len(slides))
        
        return render(request, 'index.html', {
            'comments': comments,
            'post': post,
            'slides': slides,
            'slide_indices': slide_indices
        })

class CidadesView(View):
    def get(self, request):
        cidades = Cidade.objects.all()
        return render(request, 'cidade.html', {'cidades': cidades})

class OcupacoesView(View):
    def get(self, request):
        ocupacoes = Ocupacao.objects.all()
        return render(request, 'ocupacao.html', {'ocupacoes': ocupacoes})

class UsuariosView(View):
    def get(self, request):
        usuarios = Usuario.objects.all()
        return render(request, 'usuario.html', {'usuarios': usuarios})

class EventosView(View):
    def get(self, request):
        eventos = Evento.objects.filter(data_termino__gte=date.today()).order_by("data_inicio")
        return render(request, "evento.html", {"eventos": eventos})

class AgendamentosView(View):
    def get(self, request):
        agendamentos = Agendamento.objects.all()
        return render(request, 'agendamento.html', {'agendamentos': agendamentos})

class RelatoriosView(View):
    def get(self, request):
        relatorios = Relatorio.objects.all()
        return render(request, 'relatorio.html', {'relatorios': relatorios})

class DoencasView(View):
    def get(self, request):
        return render(request, 'doenca.html')

class CalculeView(View):  # Remove LoginRequiredMixin
    template_name = "calcule.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        tipo = request.POST.get("tipo")
        valor = request.POST.get("valor")
        texto = request.POST.get("texto")

        contexto = {
            "tipo": tipo,
            "valor": valor,
            "texto": texto
        }
        return render(request, self.template_name, contexto)

    
class LoginView(View):
    template_name = 'login.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=senha)

            if user:
                login(request, user)
                return redirect('index')
            else:
                messages.error(request, "Email ou senha incorretos")

        except User.DoesNotExist:
            messages.error(request, "Email não cadastrado")

        return render(request, self.template_name)

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')

class CadastroView(View):
    template_name = "usuario.html"

    def get(self, request):
        cidades = Cidade.objects.all()
        ocupacoes = Ocupacao.objects.all()
        return render(request, self.template_name, {
            "cidades": cidades,
            "ocupacoes": ocupacoes
        })

    def post(self, request):
        nome = request.POST.get("nome")
        email = request.POST.get("email")
        senha = request.POST.get("senha")
        senha2 = request.POST.get("senha2")
        data_nasc_str = request.POST.get("data_nasc")
        cpf = request.POST.get("cpf")
        telefone = request.POST.get("telefone")
        doenca = request.POST.get("doenca")
        cidade_id = request.POST.get("cidade")
        ocupacao_id = request.POST.get("ocupacao")

        # Validações iniciais
        if senha != senha2:
            messages.error(request, "As senhas não conferem.")
            return redirect("cadastro")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Esse email já está cadastrado.")
            return redirect("cadastro")

        try:
            with transaction.atomic():
                # 🔥 CORREÇÃO: Verifica se já existe perfil para algum user
                users_existentes = User.objects.filter(email=email)
                for user_existente in users_existentes:
                    # Se existir perfil, deleta o perfil antigo
                    if hasattr(user_existente, 'usuario'):
                        print(f"🗑️ Deletando perfil antigo do user_id: {user_existente.id}")
                        user_existente.usuario.delete()

                # Cria o NOVO User
                user = User.objects.create_user(
                    username=email, 
                    email=email, 
                    password=senha
                )
                print(f"✅ Novo user criado com ID: {user.id}")

                # Processa data de nascimento
                data_nasc = None
                if data_nasc_str:
                    try:
                        data_nasc = datetime.strptime(data_nasc_str, "%Y-%m-%d").date()
                    except ValueError:
                        messages.error(request, "Data de nascimento inválida.")
                        user.delete()
                        return redirect("cadastro")

                
                cidade = Cidade.objects.get(id=cidade_id) if cidade_id else None
                ocupacao = Ocupacao.objects.get(id=ocupacao_id) if ocupacao_id else None

                
                if hasattr(user, 'usuario'):
                    print("⚠️ User já tem perfil, deletando...")
                    user.usuario.delete()

                usuario = Usuario.objects.create(
                    user=user,
                    nome=nome,
                    data_nasc=data_nasc,
                    cpf=cpf,
                    telefone=telefone,
                    doenca=doenca,
                    cidade=cidade,
                    ocupacao=ocupacao
                )
                print(f"✅ Perfil criado para user_id: {user.id}")

                messages.success(request, "Conta criada com sucesso! Faça login.")
                return redirect("login")

        except Exception as e:
            print(f"❌ Erro no cadastro: {e}")
            # Limpeza em caso de erro
            if 'user' in locals() and user.id:
                try:
                    # Tenta deletar o perfil se existir
                    if hasattr(user, 'usuario'):
                        user.usuario.delete()
                    # Deleta o user
                    user.delete()
                    print(f"🧹 User {user.id} deletado devido ao erro")
                except Exception as delete_error:
                    print(f"Erro na limpeza: {delete_error}")
            
            messages.error(request, "Erro ao criar conta. Tente novamente.")
            return redirect("cadastro")
        
        
class PerfilView(LoginRequiredMixin, View):
    template_name = "perfil.html"

    def get(self, request):
        try:
            usuario = request.user.usuario
            contexto = {
                "usuario": usuario
            }
            return render(request, self.template_name, contexto)
            
        except Usuario.DoesNotExist:
            messages.error(request, "Perfil não encontrado.")
            return redirect('index')
        
# === SISTEMA DE COMENTÁRIOS ===

class PostListView(View):
    def get(self, request):
        posts = Post.objects.all().order_by('-created_at')
        return render(request, 'blog/post_list.html', {'posts': posts})

class PostDetailView(View):
    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        comments = post.comments.filter(approved=True)
        
        context = {
            'post': post,
            'comments': comments,
        }
        return render(request, 'blog/post_detail.html', context)

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        
        # Processa o comentário manualmente
        author_name = request.POST.get('author_name', '').strip()
        text = request.POST.get('text', '').strip()
        
        # Validação básica
        if text:  # Verifica se o texto não está vazio
            comment = Comment(
                post=post,
                text=text,
                author_name=author_name
            )
            
            # Se usuário está logado, associa ao usuário
            if request.user.is_authenticated:
                comment.author = request.user
                # Se não preencheu nome, usa username
                if not author_name:
                    comment.author_name = request.user.username
            
            comment.save()
            
            # Verifica se é requisição AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'comment': {
                        'id': comment.id,
                        'author_name': comment.get_author_name(),
                        'text': comment.text,
                        'created_at': comment.created_at.strftime('%d/%m/%Y %H:%M'),
                        'likes': comment.likes
                    }
                })
            
            messages.success(request, "Comentário adicionado com sucesso!")
            return redirect('post_detail', post_id=post_id)
        else:
            # Texto vazio - mostra erro
            error = "O comentário não pode estar vazio"
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': error})
            messages.error(request, error)
            return redirect('post_detail', post_id=post_id)

class LikeCommentView(LoginRequiredMixin, View):
    def post(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        comment.likes += 1
        comment.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'likes': comment.likes})
        
        return redirect('post_detail', post_id=comment.post.id)

class DeleteCommentView(LoginRequiredMixin, View):
    def post(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        
        # Verifica se o usuário é o autor do comentário
        if comment.author == request.user or request.user.is_staff:
            post_id = comment.post.id
            comment.delete()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            
            messages.success(request, "Comentário deletado com sucesso!")
            return redirect('post_detail', post_id=post_id)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Permissão negada'})
        
        messages.error(request, "Você não tem permissão para deletar este comentário.")
        return redirect('post_detail', post_id=comment.post.id);

# views.py - ADICIONE no final do arquivo --------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class SalvarResultadoView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            tipo_calculo = data.get('tipo_calculo')
            resultado = data.get('resultado')
            
            if not tipo_calculo or not resultado:
                return JsonResponse({'success': False, 'error': 'Dados incompletos'})
            
            tipos_validos = ['imc', 'glicose', 'agua', 'pressao']
            if tipo_calculo not in tipos_validos:
                return JsonResponse({'success': False, 'error': 'Tipo de cálculo inválido'})
            
            ResultadoCalculadora.objects.create(
                usuario=request.user,
                tipo_calculo=tipo_calculo,
                resultado=resultado
            )
            
            return JsonResponse({'success': True})
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'JSON inválido'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

class MeusResultadosView(LoginRequiredMixin, View):
    def get(self, request):
        resultados = ResultadoCalculadora.objects.filter(usuario=request.user)
        return render(request, 'meus_resultados.html', {'resultados': resultados})

# views.py - MODIFIQUE a view
class DeletarResultadoView(LoginRequiredMixin, View):
    def get(self, request, resultado_id):  # Mude para GET
        try:
            resultado = get_object_or_404(ResultadoCalculadora, id=resultado_id, usuario=request.user)
            resultado.delete()
            messages.success(request, "Resultado excluído com sucesso!")
            return redirect('meus_resultados')
        except Exception as e:
            messages.error(request, f"Erro ao excluir: {str(e)}")
            return redirect('meus_resultados')