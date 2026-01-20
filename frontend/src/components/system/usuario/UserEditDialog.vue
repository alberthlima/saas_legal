<script setup>
import { 
  requiredValidator, 
  emailValidator, 
  passwordValidator, 
  selectValidator,
  optionalImageValidator,
} from '@/utils/validators'

const props = defineProps({
  isDialogVisible: {
    type: Boolean,
    required: true,
  },
  roles: {
    type: Object,
    required: true,
  },
  userSelected: {
    type: Object,
    required: true,
  }
})

const emit = defineEmits([
  'update:isDialogVisible',
  'editUser',
])

const id = ref(null);
const name = ref(null);
const surname = ref(null);
const email = ref(null);
const password = ref(null);
const role_id = ref(null);
const state = ref(null);
const avatar = ref(null);
const isLoading = ref(false);
const isPasswordVisible = ref(false);
const toast = useMaterializeToast();
const previewUrl = ref(null);

// Función para manejar la selección de imagen
const onImageSelect = (files) => {
  if (previewUrl.value && !previewUrl.value.startsWith('http')) {
    URL.revokeObjectURL(previewUrl.value)
  }
  
  const file = Array.isArray(files) ? files[0] : files
  
  if (file) {
    previewUrl.value = URL.createObjectURL(file)
  } else {
    previewUrl.value = props.userSelected.avatar || null
  }
}

const update = async() => {
  let formData = new FormData();
  formData.append('name', name.value);
  formData.append('surname', surname.value);
  formData.append('email', email.value);
  if (password.value) {
    formData.append('password', password.value);
  }
  formData.append('role_id', role_id.value);
  if (avatar.value) {
    formData.append('imagen', Array.isArray(avatar.value) ? avatar.value[0] : avatar.value);
  }
  formData.append('state', state.value);
  
  try {
    isLoading.value = true;
    
    const response = await $api("/user/" + props.userSelected.id, {
      method: "POST",
      body: formData,
      onResponse({ response }){
        console.log(response);
        if(response.status === 200){
          toast.showSuccess(
            response._data.message || 'Usuario actualizado correctamente',
            'Éxito'
          );
          // Resetear formulario
          name.value = null;
          surname.value = null;
          email.value = null;
          password.value = null;
          role_id.value = null;
          avatar.value = null;
          previewUrl.value = null;
          
          // Cerrar diálogo
          emit('update:isDialogVisible', false);
          
          // Emitir evento de actualización
          emit('editUser', response._data.user);
        } else {
          toast.showError(
            response._data.message || 'Error al actualizar el usuario',
            'Error'
          );
        }
      }
    })
  } catch (error) {
    toast.showError(
      'Error al conectar con el servidor',
      'Error'
    );
  } finally {
    isLoading.value = false;
  }
}

const onFormReset = () => {
  emit('update:isDialogVisible', false)
}

const dialogVisibleUpdate = val => {
  emit('update:isDialogVisible', val)
}

onMounted(() => {
  id.value = props.userSelected.id;
  name.value = props.userSelected.name;
  surname.value = props.userSelected.surname;
  email.value = props.userSelected.email;
  role_id.value = props.userSelected.role_id;
  state.value = props.userSelected.state;
  previewUrl.value = props.userSelected.avatar;
})

// Limpiar URL cuando el componente se destruye
onUnmounted(() => {
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
  }
})
</script>

<template>
  <VDialog
    :width="$vuetify.display.smAndDown ? 'auto' : 700 "
    :model-value="props.isDialogVisible"
    @update:model-value="dialogVisibleUpdate"
  >
    <VCard class="pa-sm-11 pa-3">
      <DialogCloseBtn
        variant="text"
        size="default"
        @click="onFormReset"
      />

      <VCardText class="pt-5">
        <div class="text-center pb-8">
          <VIcon icon="ri-folder-user-line" size="48" color="primary" class="mb-3"/>
          <h4 class="text-h4 font-weight-bold mb-2">Editar Usuario: {{ userSelected.full_name }}</h4>
        </div>

        <VForm class="mt-6" @submit.prevent="update">
          <VRow>
            <VCol cols="6">
              <VTextField v-model="name" placeholder="Ej: Pepe" label="Nombre" :rules="[requiredValidator]"/>
            </VCol>

            <VCol cols="6">
              <VTextField v-model="surname" placeholder="Ej: Perez" label="Apellido" :rules="[requiredValidator]"/>
            </VCol>

            <VCol cols="6">
              <VTextField v-model="email" placeholder="Ej: pepe@gmail.com" label="Correo Electronico" :rules="[requiredValidator, emailValidator]"/>
            </VCol>

            <VCol cols="6">
              <VTextField
                v-model="password"
                label="Password (Dejar vacío para no cambiar)"
                :type="isPasswordVisible ? 'text' : 'password'"
                :append-inner-icon="isPasswordVisible ? 'ri-eye-off-line' : 'ri-eye-line'"
                placeholder="********"
                autocomplete="new-password"
                @click:append-inner="isPasswordVisible = !isPasswordVisible"
              />
            </VCol>

            <VCol cols="6">
              <VSelect
                v-model="role_id"
                label="Rol"
                :items="props.roles"
                item-title="name"
                item-value="id"
                :rules="[selectValidator]"
              />
            </VCol>

            <VCol cols="6">
              <VSelect
                v-model="state"
                label="Estado"
                :items="[
                  {
                    name: 'Activo',
                    id: 1
                  },
                  {
                    name: 'Inactivo',
                    id: 2
                  }
                ]"
                item-title="name"
                item-value="id"
                :rules="[selectValidator]"
              />
            </VCol>

            <VCol cols="6">
              <VFileInput
                v-model="avatar"
                label="Cambiar Avatar"
                accept="image/*"
                :rules="[optionalImageValidator]"
                @update:model-value="onImageSelect"
              />
            </VCol>

            <VCol cols="6">
              <div v-if="previewUrl" class="mt-4 text-center">
                <VImg :src="previewUrl" max-width="200" max-height="200" class="mx-auto rounded-lg" cover/>
              </div>
            </VCol>
            
            <VCol cols="12" class="d-flex flex-wrap justify-center gap-4 mt-6">
              <VBtn type="submit" color="info" class="px-8" :loading="isLoading" :disabled="isLoading">
                <VIcon start icon="ri-refresh-line"/>
                <span class="font-weight-bold">{{ isLoading ? 'Actualizando...' : 'Actualizar Usuario' }}</span>
              </VBtn>

              <VBtn color="secondary" class="px-8" :disabled="isLoading" @click="onFormReset">
                <VIcon start icon="ri-arrow-left-line"/>
                <span class="font-weight-bold">Cancelar</span>
              </VBtn>
            </VCol>
          </VRow>
        </VForm>
      </VCardText>
    </VCard>
  </VDialog>
</template>