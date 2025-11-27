from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.views.generic import ListView
from django.db import transaction, IntegrityError
from django.http import JsonResponse, HttpResponseForbidden
from datetime import date, datetime

from .models import (
    Usuario,
    Cidade,
    Ocupacao,
    Evento,
    Agendamento,
    Relatorio
)

class IndexView(View):
    def get(self, request):
        return render(request, 'index.html')

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

                # Obtém cidade e ocupação
                cidade = Cidade.objects.get(id=cidade_id) if cidade_id else None
                ocupacao = Ocupacao.objects.get(id=ocupacao_id) if ocupacao_id else None

                # 🔥 CORREÇÃO: Verifica novamente antes de criar
                if hasattr(user, 'usuario'):
                    print("⚠️ User já tem perfil, deletando...")
                    user.usuario.delete()

                # Cria o Usuario
                usuario = Usuario.objects.create(
                    user=user,  # user_id será a chave primária
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