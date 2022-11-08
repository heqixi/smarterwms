<template>
  <q-card class="shadow-24">
    <q-bar
      class="bg-light-blue-10 text-white rounded-borders"
      style="height: 50px">
      <div v-if="title">
        {{ title }}
      </div>
      <div v-else>{{ $t('newtip') }}</div>
      <q-space/>
      <q-btn dense flat icon="close" v-close-popup>
        <q-tooltip content-class="bg-amber text-black shadow-4">{{
            $t('index.close')
          }}
        </q-tooltip>
      </q-btn>
    </q-bar>
    <q-card-section style="max-height: 500px; width: 400px" class="scroll">
      <div v-for="(item, index) in items" :key="index" class="q-mt-md">
        <q-uploader
          v-if="item.type === 'file'"
          :url="newFormData.url"
          method="post"
          label="请上传文件"
          batch
          :max-file-size="item.maxFileSize"
          @rejected="item.onRejected"
          @uploaded="item.onUpload"
          @added="item.onFileAdded"
          :headers="[{ name: 'token', value: token }]"
          :field-name="file => file.name"
        >
        </q-uploader>
        <q-select
          v-else-if="item.type === 'select'"
          filled
          v-model="newFormData[item.field]"
          :options="item.options"
          clearable
          new-value-mode="add-unique"
          use-input
          :label="item.label"
          :option-label="item.optionLabel"
          :hint="item.hint">
          <template v-if="item.newValue" v-slot:append>
            <q-btn round dense flat icon="add" @click.stop="item.newValue"/>
          </template>
        </q-select>
        <q-toggle
          v-else-if="item.type === 'toggle'"
          v-model="newFormData[item.field]"
          :label="item.label"
          color="green"
        />
        <q-input
          v-else-if="item.edit"
          dense
          square
          v-model="newFormData[item.field]"
          :label="item.label"
          autofocus
          :rules="[val => val && val.length > 0]"
          @keyup.enter="newDataSubmit()"
        />
        <div v-else>
          <q-field :label="item.label" stack-label>
            <template v-slot:control>
              <div class="self-center full-width no-outline" tabindex="0">
                {{ _getFieldValue(newFormData, item) }}
              </div>
            </template>
          </q-field>
        </div>
      </div>
    </q-card-section>
    <div v-if="!hideBottom" style="float: right; padding: 15px 15px 15px 0">
      <q-btn
        color="white"
        text-color="black"
        style="margin-right: 25px"
        @click="newDataCancel()"
      >{{ $t('cancel') }}
      </q-btn>
      <q-btn color="primary" @click="newDataSubmit()">{{ $t('submit') }}</q-btn>
    </div>
  </q-card>
</template>
<script>
import { LocalStorage } from 'quasar'

export default {
  name: 'NewForm',
  data () {
    return {
      token: LocalStorage.getItem('openid')
    }
  },
  methods: {
    _getFieldValue (item, column) {
      let targetField = item
      if (column.field !== 'self') {
        targetField = item[column.field]
      }
      const value = column.fieldMap ? column.fieldMap(targetField) : targetField
      if (column.field === 'self') {
        console.log('_getFieldValue self ,', column, value)
      }
      return value
    },
    newDataSubmit () {
      console.log('newDataSubmit ')
      this.$emit('newDataSummit', this.newFormData)
    },
    newDataCancel () {
      console.log('newDataCancel')
      this.$emit('newDataCancel')
    },
  },
  created () {
    console.log('new form items ', this.items, ' data', this.newFormData, ',hide bottom ', this.hideBottom)
  },
  props: ['items', 'newFormData', 'hideBottom', 'title']
}
</script>
