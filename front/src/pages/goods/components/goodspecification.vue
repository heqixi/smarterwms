<template>
  <q-card>
    <q-banner inline-actions class="text-white bg-blue-5">规格信息</q-banner>
    <q-card-section class="row justify-start">
      <div class="q-gutter-sm">
        <q-radio left-label v-model="mode" val="singleSku" label="单品"/>
        <q-radio left-label v-model="mode" val="multipleSku" label="多规格"/>
      </div>
      <div class="col-2 q-ml-lg">
        <q-btn
          v-if="mode === 'multipleSku'"
          :disable="specifications.filter((spec) => {return !spec.is_delete}).length >= 2"
          @click="addSpecification">添加规格
        </q-btn>
      </div>

    </q-card-section>

    <q-card-section v-if="mode === 'multipleSku'">
      <q-list
        class="row justify-start"
        v-for="(specification, index) in specifications.filter(spec => {return !spec.is_delete})"
        :key="index">
        <q-input
          class="col-2"
          dense
          square
          autofocus
          v-model="specification.name"
          label="请输入规格名称"
          @click="specification.edit = true"
          @blur="onSpecificationUpdate(specification)"
          :rules="[val => (val && val.length > 0) || error1]">
          <template v-slot:before class="q-mb-sm">
            <span v-if="specification.require" :style="{color:'red', fontSize:'8px'}"> * </span>
            <div class="text-body2">
              规格名称
            </div>
          </template>
          <template v-slot:after class="q-mb-sm">
            <q-icon
              dense
              name="close"
              @click="removeSpecification(specification)"
              class="cursor-pointer"
            />
          </template>
        </q-input>
        <div class="col-1.5 q-ml-lg">
          <q-btn-group push >
            <q-btn
              :disable="specification.options.length >= 50"
              @click="addOptions(specification, index)">添加选项
            </q-btn>
            <q-btn
              :disable="specification.options.length >= 50"
              @click="batchAddOption(specification, index)">批量添加
            </q-btn>
            <q-btn
              @click="batchEditOptionName(specification.options)">批量编辑
            </q-btn>
          </q-btn-group>
        </div>
        <q-list
          class="row"
          v-for="(option, optionIndex) in specification.options"
          :key="optionIndex">
          <q-chip
            v-if="!option.is_delete"
            class="col"
            removable
            v-model="option.show"
            @remove="removeOption(specification,  option)"
            text-color="black">
            <q-input
              v-if="option.edit"
              v-model="option.name"
              :rules="[(name) => optionNameRule(specification, name)]"
              autofocus
              @keydown.enter="editOption(option)"
              @blur="editOption(option)">
            </q-input>
            <div v-else @click="clickOptionName(option)">
              {{ option.name }}
            </div>
          </q-chip>
        </q-list>
      </q-list>

      <div class="row q-mt-sm" v-show="pickImage">
        <span :style="{color:'red', fontSize:'8px'}"> * </span>
        <div class="text-body2">
          采集图片
        </div>
      </div>
      <div class="q-mt-sm row items-start" v-if="pickImage">
        <q-img
          draggable="true"
          @dragstart="onOptionImageDragStart"
          v-for="(image, index) in imageOptions"
          :id="'option-' + image.id"
          :key="index"
          :src="image.url"
          style="width: 120px"
          ratio="1"
          spinner-color="white"
          class="rounded-borders q-mr-sm q-mt-sm">
        </q-img>
      </div>
      <div class="row" v-if="pickImage">
        <q-btn class="col-12"  @click="pickImage=false">
          收起
        </q-btn>
      </div>
      <div class="row q-mt-sm">
        <span :style="{color:'red', fontSize:'8px'}"> * </span>
        <div class="text-body2">
          变体图
        </div>
      </div>
      <div class="row q-mt-sm"
           v-if="specifications.length > 0 && specifications[0].options.length > 0"
           @dragenter="onDragEnter"
           @dragleave="onDragLeave"
           @dragover="onDragOver"
           @drop="onDrop">
        <div v-for="(option, index) in specifications[0].options.filter(opt => {return !opt.is_delete})"
             :key=index
             class="col-1.5 q-mr-sm">
          <q-card
            :id="index"
            class="image-card q-mb-sm">
            <q-img
              v-if="option.image"
              :id="index"
              draggable="true"
              @dragstart="onImageDragStart"
              :src="option.image"
              style="width: 120px"
              ratio="1"
              spinner-color="white"
              class="rounded-borders">
              <q-icon class="absolute all-pointer-events"
                      dense
                      size="32px" name="clear" color="red" style="top: 8px; right: 8px"
                      @click="deleteImge(option)">
                <q-tooltip>
                  删除
                </q-tooltip>
              </q-icon>
            </q-img>
            <div v-else class="row" :style="{height: '120px', width:'120px'}">
              <q-btn class="col-12 text-caption" flat @click="choseImage()">选择采集图片</q-btn>
              <q-btn class="col-12 text-caption" flat @click="uploadImage(option, index)">本地上传</q-btn>
              <q-btn class="col-12 text-caption" flat>图片链接</q-btn>
            </div>
          </q-card>
          <div v-if="!option.is_delete" class="text-center text-caption">{{ option.name }}</div>
        </div>
      </div>
    </q-card-section>

    <q-table
      title="库存设置"
      :data="models.filter(model => {return !model.is_delete})"
      :columns="columns"
      row-key="name"
      binary-state-sort>
      <template v-slot:top="props">
        <div class="col-0.8 q-table__title">库存设置</div>
        <div class="col q-ml-md text-body2">
          <q-btn icon="refresh" @click="refreshModels">
            刷新变体
          </q-btn>
        </div>
      </template>
      <template v-slot:header-cell-name="props">
        <q-th :props="props">
          <div @click="editModelName(props.col)">
            {{ props.col.label }}
            <q-icon name="edit" size="1.2em"/>
          </div>
        </q-th>
      </template>
      <template v-slot:header-cell-price="props">
        <q-th :props="props">
          <div @click="batchEditModelPrice(props.col)">
            {{ props.col.label }}
            <q-icon name="edit" size="1.2em"/>
          </div>
        </q-th>
      </template>
      <template v-slot:header-cell-stock="props">
        <q-th :props="props">
          <div @click="batchEditModelStock(props.col)">
            {{ props.col.label }}
            <q-icon name="edit" size="1.2em"/>
          </div>
        </q-th>
      </template>
      <template v-slot:body="props">
        <q-tr :props="props">
          <q-td key="name" :props="props">
            {{ props.row.name }}
            <q-popup-edit v-model="props.row.name" v-slot="scope">
              <q-input
                v-model="scope.value"
                dense
                counter
                :rules="[val => (val && val.length > 0) || error1]"
              />
            </q-popup-edit>
          </q-td>
          <q-td key="code" :props="props">
            <q-input
              v-model="props.row.code"
              dense
              :rules="[val => (val && val.length > 0) || error1]"
            />
          </q-td>
          <q-td key="price" :props="props">
            <q-input
              type="number"
              v-model="props.row.stock.price"
              dense
              :rules="[val => (val && val > 0) || error3]"
              @input="value => {props.row.update=true}"
            />
          </q-td>
          <q-td key="stock" :props="props">
            <q-input
              type="number"
              v-model="props.row.stock.stock_qty"
              dense
              :rules="[val => (val && val > 0) || error3]"
              @input="value => {props.row.update=true}"
            />
          </q-td>
          <q-td key="sku" :props="props">
            <q-input
              v-model="props.row.sku"
              dense
              :rules="[val => (val && val.length > 0) || error5]"
            />
          </q-td>
          <q-td key="goods_code" :props="props">
            <q-field>
              <template v-slot:control>
                <div class="self-center full-width no-outline" tabindex="0">{{props.row.goods_code}}</div>
              </template>
              <template v-if="!props.row.add" v-slot:after class="q-mb-sm">
                <q-icon
                  dense
                  name="refresh"
                  @click="changedGoods(props.row)"
                  class="cursor-pointer"
                />
                <q-icon
                  dense
                  name="delete"
                  @click="deleteGoodsMapping(props.row)"
                  class="cursor-pointer"
                />
              </template>
            </q-field>
          </q-td>
        </q-tr>
      </template>
    </q-table>
  </q-card>
</template>

<script>
import UploadImageDialog from 'pages/goods/components/uploadImageDialog'
import { getauth, postauth } from 'boot/axios_request'
import SelectStore from 'pages/goods/components/selectstoredialog'
import GoodsEditPriceDialog from 'pages/goods/components/goodsPriceEdit'
import { CURRENCY_CODE } from 'src/store/goods/types'
import NewFormDialog from 'components/Share/newFormDialog'
import goodssearch from 'pages/order/components/goodssearch'

export default {
  name: 'GoodSpecification',
  data () {
    return {
      mode: 'multipleSku',
      batchUpdata: {
        namePrefix: '',
        nameNumPrefix: false,
        nameLetterPrefix: false,
        num: 0,
        stock_qty: 0,
        price: 0
      },
      columns: [
        {
          name: 'name',
          require: true,
          label: '规格名称',
          align: 'center',
          field: 'name',
          edit: false,
          prefix: '',
          format: val => `${val}`,
          sortable: false
        },
        {
          name: 'price',
          require: true,
          label: '价格',
          align: 'center',
          field: 'price',
          sortable: false
        },
        {
          name: 'stock',
          require: true,
          label: '库存',
          align: 'center',
          field: 'stock',
          sortable: false
        },
        {
          name: 'sku',
          require: true,
          label: 'SKU',
          align: 'center',
          field: model => model.sku,
          sortable: false
        },
        {
          name: 'goods_code',
          require: true,
          label: '关联货物编号',
          align: 'center',
          field: 'goods_code',
          sortable: false
        }
      ],
      pickImage: false,
      error1: '请输入规格名称',
      error2: '请输入SKU',
      error3: '请输入价格',
      error4: '请输入库存数量',
      error5: '请输入货号'
    }
  },
  watch: {
    mainSku: function (val) {
      this.models.forEach(model => {
        model.sku = this.mainSku + '-' + model.name
        model.update = true
      })
    }
  },
  methods: {
    deleteGoodsMapping (model) {
      const formData = {
        product: model.id
      }
      postauth('goods/product/unbind_goods', formData).then(res => {
        this.$q.notify({
          message: '更改绑定成功',
          icon: 'check',
          color: 'green'
        })
        model.goods_code = ''
      })
    },
    changedGoods (model, is_delete = false) {
      console.log('change goods ', model)
      this.$q.dialog({
        component: goodssearch
      }).onOk(goodsList => {
        console.log('change to goods ', goodsList)
        if (goodsList.length <= 0 || goodsList.length > 1) {
          this.$q.notify({
            message: '只能选择一个产品',
            icon: 'check',
            color: 'green'
          })
          return
        }
        const selectGoods = goodsList[0]
        const formData = {
          product: model.id,
          goods: selectGoods.id,
        }
        postauth('goods/product/bind_goods', formData).then(res => {
          this.$q.notify({
            message: '更改绑定成功',
            icon: 'check',
            color: 'green'
          })
          model.goods_code = selectGoods.goods_code
        })
      })
    },
    refreshModels () {
      const specs = this.specifications.filter(spec => { return !spec.is_delete })
      console.log('refresh model, specs ', specs)
      for (let i = this.models.length - 1; i >= 0; i--) {
        const model = this.models[i]
        if (model.is_delete) {
          continue
        }
        const modelOptions = model.options
        let isValid = true
        if (modelOptions.length <= 0 || !(modelOptions.length === specs.length)) {
          isValid = false
        }
        for (let j = 0; j < modelOptions.length; j++) {
          const optionSpec = modelOptions[j].specification
          if (!specs.find(spec => { return spec.id === optionSpec.id })) {
            isValid = false
            break
          }
        }
        if (!isValid) {
          console.log('model ', model, ', is not valid ')
          if (model.add) {
            this.models.splice(i, 1)
          } else {
            model.is_delete = true
            model.update = true
          }
        } else {
          console.log('model is valid ', model)
        }
      }
      const validatedModels = this.models.filter(model => { return !model.is_delete })
      console.log('models length ', this.models.length, ', validatedModels length ', validatedModels.length)
      if (specs.length <= 1 && specs[0].options.length > 0) {
        specs[0].options.forEach(opt => {
          if (!validatedModels.find(model => { return model.options[0].id === opt.id })) {
            this.models.unshift({
              name: opt.name,
              image: opt.image,
              code: '',
              stock: {
                stock_qty: undefined,
                price: undefined
              },
              sku: '',
              options: [opt],
              add: true
            })
          }
        })
      } else {
        specs[0].options.forEach(optFirst => {
          specs[1].options.forEach(optSecond => {
            const existModel = validatedModels.find(model => {
              const modelOptFirst = model.options.find(opt => {
                return opt.specification.id === specs[0].id
              })
              const modelOptSecond = model.options.find(opt => {
                return opt.specification.id === specs[1].id
              })
              return modelOptFirst.id === optFirst.id && modelOptSecond.id === optSecond.id
            })
            if (!existModel) {
              // model 不存在，需要新建，一般来说不存在这种情况
              this.models.unshift({
                name: optFirst.name + '-' + optSecond.name,
                image: optFirst.image,
                code: '',
                stock: {
                  stock_qty: undefined,
                  price: undefined
                },
                sku: '',
                options: [optFirst, optSecond],
                add: true
              })
            }
          })
        })
      }
    },
    clickOptionName (option) {
      this.$set(option, 'edit', true)
    },
    deleteModel (model, index) {
      if (model.add) {
        const validModels = this.model.filter(model => { return !model.is_delete })
        if (index >= 0 && index < validModels.length) {
          validModels.splice(index, 1)
        }
      } else {
        model.is_delete = true
        model.update = true
      }
    },
    batchEditOptionName (options) {
      console.log('batch edit option ', options)
      var _this = this
      const formItems = [
        {
          name: 'name_prefix',
          label: '前缀',
          type: 'text',
          field: 'namePrefix',
          edit: true
        },
        {
          name: 'name_num_prefix',
          label: '数字前缀',
          type: 'toggle',
          field: 'nameNumPrefix',
          edit: true
        }
        // {
        //   name: 'name_letter_prefix',
        //   label: '字母前缀',
        //   type: 'toggle',
        //   field: 'nameLetterPrefix',
        //   edit: true
        // }
      ]
      _this.batchUpdata.namePrefix = ''
      _this.batchUpdata.nameNumPrefix = false
      _this.batchUpdata.nameLetterPrefix = false
      _this.$q.dialog({
        component: NewFormDialog,
        title: '请输入前缀',
        newFormData: _this.batchUpdata,
        newFormItems: formItems
      }).onOk(() => {
        console.log('batch update model name  ', _this.batchUpdata)
        _this.addNamePrefix2Option(options)
      })
    },
    addNamePrefix2Option (options) {
      var _this = this
      options.filter(option => { return !option.is_delete }).forEach((option, index) => {
        let optionName = ''
        if (this.batchUpdata.nameNumPrefix) {
          optionName += (index + 1) + '-'
        }
        if (this.batchUpdata.namePrefix && this.batchUpdata.namePrefix.length > 0) {
          optionName += this.batchUpdata.namePrefix + '-'
        }
        if (!option.originName) {
          option.originName = option.name
        }
        optionName += option.originName
        _this.$set(option, 'name', optionName)
        option.update = true
        _this.editOption(option)
      })
    },
    editModelName (col) {
      console.log('edit model name ', col)
      var _this = this
      this.$set(col, 'edit', true)
      const formItems = [
        {
          name: 'name_prefix',
          label: '前缀',
          type: 'text',
          field: 'namePrefix',
          edit: true
        },
        {
          name: 'name_num_prefix',
          label: '数字前缀',
          type: 'toggle',
          field: 'nameNumPrefix',
          edit: true
        }
        // {
        //   name: 'name_letter_prefix',
        //   label: '字母前缀',
        //   type: 'toggle',
        //   field: 'nameLetterPrefix',
        //   edit: true
        // }
      ]
      _this.batchUpdata.namePrefix = ''
      _this.batchUpdata.nameNumPrefix = false
      _this.batchUpdata.nameLetterPrefix = false
      _this.$q.dialog({
        component: NewFormDialog,
        title: '请输入前缀',
        newFormData: _this.batchUpdata,
        newFormItems: formItems
      }).onOk(() => {
        console.log('batch update model name  ', _this.batchUpdata)
        _this.addNamePrefix2Model()
      })
    },
    batchEditModelPrice (col) {
      console.log('edit model price ', col)
      var _this = this
      const formItems = [
        {
          name: 'stock_num',
          label: '成本价',
          type: 'text',
          field: 'price',
          edit: true
        }
      ]
      _this.batchUpdata.stock_qty = 0
      _this.$q.dialog({
        component: NewFormDialog,
        title: '请输入价格信息',
        newFormData: _this.batchUpdata,
        newFormItems: formItems
      }).onOk(() => {
        console.log('batch update price  ', _this.batchUpdata)
        const batchPrice = parseFloat(_this.batchUpdata.price)
        if (batchPrice > 0) {
          _this.models.filter(model => {
            return !model.is_delete
          }).forEach(model => {
            const modelStock = model.stock
            _this.$set(modelStock, 'price', batchPrice)
            model.update = true
          })
        } else {
          this.$q.notify({
            message: '价格必须大于0',
            icon: 'close',
            color: 'negative'
          })
        }
      })
    },
    batchEditModelStock (col) {
      console.log('edit model stock ', col)
      var _this = this
      const formItems = [
        {
          name: 'stock_num',
          label: '库存数量',
          type: 'text',
          field: 'stock_qty',
          edit: true
        }
      ]
      _this.batchUpdata.stock_qty = 0
      _this.$q.dialog({
        component: NewFormDialog,
        title: '请输入库存数量',
        newFormData: _this.batchUpdata,
        newFormItems: formItems
      }).onOk(() => {
        console.log('batch update stock qty  ', _this.batchUpdata)
        const batchQty = parseInt(_this.batchUpdata.stock_qty)
        if (batchQty > 0 && batchQty < 10000) {
          _this.models.filter(model => {
            return !model.is_delete
          }).forEach(model => {
            const modelStock = model.stock
            _this.$set(modelStock, 'stock_qty', batchQty)
            model.update = true
          })
        } else {
          this.$q.notify({
            message: '单个库存数量不大于10000',
            icon: 'close',
            color: 'negative'
          })
        }
      })
    },
    addNamePrefix2Model () {
      var _this = this
      this.models.filter(model => {
        return !model.is_delete
      }).forEach((model, index) => {
        let modelName = ''
        if (this.batchUpdata.nameNumPrefix) {
          modelName += (index + 1) + '-'
        }
        if (this.batchUpdata.namePrefix && this.batchUpdata.namePrefix.length > 0) {
          modelName += this.batchUpdata.namePrefix + '-'
        }
        if (model.options.length === 1) {
          modelName += model.options[0].name
        } else if (model.options.length >= 2) {
          modelName += model.options[0].name + '-' + model.options[1].name
        }
        _this.$set(model, 'name', modelName)
        model.update = true
      })
    },
    addSpecification () {
      if (this.specifications.length > 0) {
        const spec = this.specifications[0]
        if (!spec.name || spec.name.length <= 0) {
          this.$q.notify({
            message: '请先完善第一个规格名称',
            icon: 'close',
            color: 'negative'
          })
          return
        }
      }
      const existMaxId = this.specifications.reduce((maxId, spec) => {
        return Math.max(maxId, spec.id)
      }, 0)
      this.specifications.push({
        name: '',
        id: existMaxId + 1,
        edit: true,
        valid: false,
        require: true,
        index: this.specifications.length,
        options: [],
        add: true
      })
    },
    onSpecificationUpdate (spec) {
      if (spec.name != null) {
        const anotherSpec = this.specifications.find(specification => {
          if (specification.id !== spec.id) {
            return specification
          }
        })
        if (anotherSpec && anotherSpec.name === spec.name) {
          this.$q.notify({
            message: '规格名称不能重复',
            icon: 'close',
            color: 'negative'
          })
          spec.name = ''
        }
      }
      spec.update = true
    },
    removeSpecification (spec) {
      console.log('removeSpecification, ', spec)
      for (var i = spec.options.length - 1; i >= 0; i--) {
        this.removeOption(spec, spec.options[i])
      }
      this.specifications.forEach((specification, index) => {
        if (specification.id === spec.id) {
          if (spec.add) {
            this.specifications.splice(index, 1)
          } else {
            const specificationRemove = this.specifications.splice(index, 1)[0]
            specificationRemove.is_delete = true
            specificationRemove.update = true
            this.$emit('removeSpec', specificationRemove)
          }
        }
      })
    },
    optionNameRule (spec, optonName) {
      const existOption = spec.options.find(option => { return option.name === optonName })
      console.log('option name validatet ,', spec, optonName, existOption)
      return !existOption
    },
    editOption (option) {
      if (option.name.length > 0) {
        option.valid = true
      }
      option.edit = false
      option.update = true
      let specIndex = -1
      this.specifications.forEach((spec, index) => {
        if (spec.id === option.specification.id) {
          specIndex = index
        }
      })
      if (specIndex < 0) {
        throw new Error('Can not find spec for option ')
      }
      for (var i = 0; i < this.models.length; i++) {
        const model = this.models[i]
        console.log('edit option ', specIndex, model, option)
        if (specIndex === 0 && model.options[0].id === option.id) {
          model.name = model.options[1] ? option.name + '-' + model.options[1].name : option.name
          model.sku = this.mainSku + '-' + model.name
          model.update = true
        }
        if (specIndex === 1 && model.options[1].id === option.id) {
          // model.name = model.optionFirst ? model.optionFirst.name + '-' + option.name : option.name
          model.name = model.options[0] ? model.options[0].name + '-' + option.name : option.name
          model.update = true
          model.sku = this.mainSku + '-' + model.name
          model.update = true
        }
      }
    },
    batchAddOption (spec, specIdx) {
      var _this = this
      const formItems = [
        {
          name: 'name_prefix',
          label: '前缀',
          type: 'text',
          field: 'namePrefix',
          edit: true
        },
        {
          name: 'option_num',
          label: '数量',
          type: 'number',
          field: 'num',
          edit: true
        }
      ]
      _this.batchUpdata.namePrefix = ''
      _this.batchUpdata.num = 0
      _this.batchUpdata.nameNumPrefix = false
      _this.batchUpdata.nameLetterPrefix = false
      _this.$q.dialog({
        component: NewFormDialog,
        title: '请输入选项信息',
        newFormData: _this.batchUpdata,
        newFormItems: formItems
      }).onOk(() => {
        console.log('batch update model name  ', _this.batchUpdata)
        const optionNum = parseInt(_this.batchUpdata.num)
        for (let i = 1; i < optionNum + 1; i++) {
          const option = _this.addOptions(spec, specIdx)
          _this.$set(option, 'name', _this.batchUpdata.namePrefix + '-' + i)
          _this.editOption(option)
        }
      })
    },
    addOptions (spec, spcIndex) {
      if (spcIndex > 1) {
        this.$q.notify({
          message: '出错了，规格多于2个，请重试',
          icon: 'close',
          color: 'negative'
        })
        return
      }
      if (!spec.name || spec.name.length <= 0) {
        this.$q.notify({
          message: '请先完善规格名称',
          icon: 'close',
          color: 'negative'
        })
        return
      }
      if (spcIndex === 1 && this.specifications[0].options.length <= 0) {
        this.$q.notify({
          message: `先先为 ${this.specifications[0].name} 增加选项`,
          icon: 'close',
          color: 'negative'
        })
        return
      }
      let existMaxOptionId = 0
      this.specifications.forEach(existSpec => {
        existMaxOptionId = existSpec.options.reduce((maxId, option) => {
          return Math.max(maxId, option.id)
        }, existMaxOptionId)
      })
      const option = {
        name: '',
        id: existMaxOptionId + 1,
        edit: true,
        valid: false,
        image: undefined,
        specification: spec,
        index: spec.options.length,
        add: true
      }
      spec.options.push(option)
      let firstOption = null
      let secondOption = null
      if (spcIndex === 0) {
        firstOption = option
      } else {
        secondOption = option
      }
      console.log('add option spcIndex ', spcIndex)
      if (this.specifications.length < 2) {
        console.log('add option spcIndex only one spec')
        this.models.push(
          {
            name: firstOption ? firstOption.name : secondOption.name,
            valid: false,
            code: '',
            stock: {
              stock_qty: undefined,
              price: undefined
            },
            sku: '',
            options: [firstOption, secondOption],
            add: true
          }
        )
      } else if (spcIndex === 0) {
        console.log('add option of first spec ')
        const secondLevelOptons = this.specifications[1].options
        if (secondLevelOptons.length > 0) {
          const firstSpecOptions = this.specifications[0].options
          if (firstSpecOptions.length === 1) {
            this.models.forEach(model => {
              // model.optionFirst = firstSpecOptions[0]
              model.options[0] = firstSpecOptions[0]
              model.update = true
            })
          } else {
            secondLevelOptons.forEach(option => {
              this.models.push({
                name: firstOption.name + '-' + option.name,
                image: undefined,
                code: '',
                stock: {
                  stock_qty: undefined,
                  price: undefined
                },
                sku: '',
                options: [firstOption, option],
                add: true
              })
            })
          }
        } else {
          this.models.push(
            {
              name: firstOption.name,
              image: undefined,
              code: '',
              stock: {
                stock_qty: undefined,
                price: undefined
              },
              sku: '',
              options: [firstOption, null],
              add: true
            }
          )
        }
      } else {
        const firstSpecificationOptons = this.specifications[0].options
        if (firstSpecificationOptons.length > 0) {
          const secondSpecOptions = this.specifications[1].options
          if (secondSpecOptions.length === 1) {
            this.models.forEach(model => {
              // model.optionSecond = secondSpecOptions[0]
              model.options[1] = secondSpecOptions[0]
              model.update = true
            })
          } else {
            firstSpecificationOptons.forEach(option => {
              this.models.push({
                name: option.name + '-' + secondOption.name,
                image: undefined,
                code: '',
                stock: {
                  stock_qty: undefined,
                  price: undefined
                },
                sku: '',
                options: [option, secondOption],
                add: true
              })
            })
          }
        } else {
          this.models.push(
            {
              name: secondOption.name,
              image: undefined,
              code: '',
              stock: {
                stock_qty: undefined,
                price: undefined
              },
              sku: '',
              options: [null, secondOption],
              add: true
            }
          )
        }
      }
      return option
    },
    removeOption (spec, option) {
      console.log('remove option ', spec, option)
      let specIndex = -1
      this.specifications.forEach((specification, index) => {
        if (spec.id === specification.id) {
          specIndex = index
        }
      })
      if (specIndex < 0) {
        throw new Error('Can not find spec for option ')
      }
      console.log('beofore remove , ', spec.options.length, this.models.length)
      const validOptions = spec.options.filter(option => { return !option.is_delete })
      const validSpec = this.specifications.filter(spec => { return !spec.is_delete })
      if (validOptions.length === 1 && validSpec.length > 1) {
        // 规格中最后一个Option
        this.models.forEach(model => {
          if (specIndex === 0) {
            model.name = model.options[1].name
            model.options[0] = null
          } else {
            model.name = model.options[0].name
            model.options[1] = null
          }
        })
      } else {
        for (var i = this.models.length - 1; i >= 0; i--) {
          const optionId = option.id
          const modelAt = this.models[i]
          if ((modelAt.options[0] && modelAt.options[0].id === optionId) ||
            (modelAt.options[1] && modelAt.options[1].id === optionId)) {
            if (this.models[i].add) {
              this.models.splice(i, 1)
            } else {
              this.models[i].is_delete = true
              this.models[i].update = true
            }
          }
        }
      }
      spec.options.forEach((opt, index) => {
        if (opt.id === option.id) {
          if (opt.add) {
            // 新加的option 直接移出，无须更新服务器
            spec.options.splice(index, 1)
          } else {
            opt.is_delete = true
            opt.update = true
          }
        }
      })
    },
    onOptionImageDragStart (e) {
      console.log('on option drop start')
      e.dataTransfer.setData('optionImageId', e.target.id)
      e.dataTransfer.dropEffect = 'move'
    },
    onDragEnter (e) {
      // don't drop on other draggables
      // console.log('on drags enter ', e)
      if (e.target.draggable !== true) {
        e.target.classList.add('drag-enter')
      }
    },
    choseImage () {
      this.pickImage = true
      this.$q.notify({
        message: '请直接拖拽图片到你想要的位置',
        icon: 'check',
        color: 'green'
      })
    },
    uploadImage (option, index) {
      const _this = this
      _this.$q.dialog({
        component: UploadImageDialog,
        maxFiles: 50
      }).onOk((imagesInfos) => {
        const options = _this.specifications[0].options.filter(opt => { return !opt.is_delete })
        for (let i = index; i < options.length; i++) {
          if (i - index + 1 > imagesInfos.length) {
            break
          }
          const optionAt = options[i]
          const imageInfo = imagesInfos[i - index]
          _this.$set(optionAt, 'image', imageInfo.url)
          let optionMedia = optionAt.option_media
          if (!optionMedia) {
            console.warn('Option missing option media ', optionAt)
            optionMedia = {}
          }
          optionMedia.url = imageInfo.url
          optionMedia.media = imageInfo.id
          optionAt.option_media = optionMedia
          optionAt.update = true
          _this.updateModelImage(optionAt)
        }
      })
    },
    deleteImge (option) {
      console.log('delete model ', option)
      this.$set(option, 'image', undefined)
      option.image = undefined
      option.update = true
      this.updateModelImage(option)
    },
    onDragLeave (e) {
      e.target.classList.remove('drag-enter')
    },
    onDragOver (e) {
      // console.log('on drags over ', e)
      e.preventDefault()
    },
    onImageDragStart (e) {
      e.dataTransfer.setData('optionId', e.target.id)
      e.dataTransfer.dropEffect = 'move'
    },
    onDrop (e) {
      e.preventDefault()
      // don't drop on other draggables
      if (e.target.draggable === true) {
        return
      }
      const optionImageEleId = e.dataTransfer.getData('optionImageId')
      const optionId = e.dataTransfer.getData('optionId')
      const elementId = optionImageEleId || optionId
      const draggedEl = document.getElementById(elementId)
      // check if original parent node
      if (draggedEl.parentNode === e.target) {
        e.target.classList.remove('drag-enter')
        return
      }
      const cardId = this.findTargetImageIndex(e.target, 0, 10)
      console.log('drag image ', optionImageEleId, cardId)
      if (optionId) {
        this.exchangeModelImage(optionId, cardId)
      } else if (optionImageEleId) {
        this.addDragImage(cardId, optionImageEleId.split('-')[1])
      }
      e.target.classList.remove('drag-enter')
    },
    exchangeModelImage (from, to) {
      const options = this.specifications[0].options
      const validOptions = options.filter(model => {
        return !model.is_delete
      })
      const fromOption = validOptions[from]
      const toOption = validOptions[to]
      const tmpUrl = toOption.image
      toOption.image = fromOption.image
      fromOption.image = tmpUrl
      const toOptionMedia = toOption.option_media || {}
      const fromOptionMedia = fromOption.option_media || {}
      toOption.option_media = toOptionMedia
      fromOption.option_media = fromOptionMedia
      toOption.option_media.url = fromOptionMedia.url
      toOption.option_media.media = fromOptionMedia.media
      fromOption.option_media.url = toOptionMedia.url
      fromOption.option_media.media = toOptionMedia.media
      fromOption.option_media.update = true
      toOption.option_media.update = true
      fromOption.update = true
      toOption.update = true
      this.updateModelImage(fromOption)
      this.updateModelImage(toOption)
    },
    addDragImage (cardId, imageOptionId) {
      const options = this.specifications[0].options
      const validOptions = options.filter(model => {
        return !model.is_delete
      })
      console.log('add dray image ', cardId, imageOptionId, validOptions)
      const option = validOptions[cardId]
      const imageOption = this.imageOptions.find(image => {
        return (image.id + '') === imageOptionId
      })
      this.$set(option, 'image', imageOption.url)
      const optionMedia = option.option_media || {}
      optionMedia.url = imageOption.url
      optionMedia.media = undefined
      optionMedia.update = true
      option.option_media = optionMedia
      option.update = true
      this.updateModelImage(option)
    },
    updateModelImage (option) {
      this.models.forEach(model => {
        if (model.options.length > 0 && model.options[0].id === option.id) {
          model.image = option.image
        }
      })
      console.log('after update model image ', option, this.models)
    },
    findTargetImageIndex (htmlEl, depth, maxDepth) {
      if (depth > maxDepth) {
        console.log('target html not found')
        return ''
      }
      const outerHTML = htmlEl.outerHTML
      if (outerHTML.indexOf('image-card') > 0) {
        return htmlEl.id
      }
      return this.findTargetImageIndex(htmlEl.parentNode, depth + 1, 10)
    },
    async editPriceInfo () {
      const storeList = await getauth('store/all?type=2', {})
      console.log('get store list ', storeList)
      const storeGroups = []
      storeList.forEach(store => {
        let existGroup = storeGroups.find(group => { return group.area === store.area })
        if (!existGroup) {
          existGroup = {
            area: store.area,
            storeList: [],
            selected: undefined
          }
          storeGroups.push(existGroup)
        }
        existGroup.storeList.push(store)
      })
      var _this = this
      _this.$q.dialog({
        component: SelectStore,
        data: storeGroups,
        title: '请选择店铺'
      }).onOk(selectedShoped => {
        console.log('select shop', selectedShoped)
        if (selectedShoped.length <= 0) {
          _this.$q.notify({
            message: '请至少选择一个店铺',
            icon: 'close',
            color: 'negative'
          })
          return
        }
        const productPriceInfo = []
        selectedShoped.forEach(store => {
          const models = JSON.parse(JSON.stringify(_this.models))
          models.forEach(model => {
            const storePrice = model.price_info.find(priceInfo => {
              return priceInfo.store_id === store.uid
            })
            const currentPrice = storePrice ? storePrice.current_price : 0
            const originalPrice = storePrice ? storePrice.original_price : 0
            const discount = storePrice ? { discount_id: storePrice.discount_id } : { discount_id: 0 }
            if (!model.current_price) {
              _this.$set(model, 'current_price', currentPrice)
              _this.$set(model, 'discount', discount)
            }
            if (!model.original_price) {
              _this.$set(model, 'original_price', originalPrice)
            }
            model.model_id = store.uid + '_' + model.sku
          })
          const priceInfo = {
            area: store.area,
            // image: _this.product.image,
            // sku: _this.product.sku,
            models: models,
            currency: CURRENCY_CODE[store.area],
            type: 'shopee',
            store_id: store.uid,
            store_name: store.name,
            discount: undefined,
            store: store
          }
          productPriceInfo.push(priceInfo)
        })
        _this.$q.dialog({
          component: GoodsEditPriceDialog,
          products: productPriceInfo,
          rowKey: 'store_id',
          modelKey: 'sku',
          editOriginalPrice: true,
          tableStyle: {
            width: '1500px',
            maxWidth: '1500px'
          }
        }).onOk((priceInfos) => {
          console.log('edit priece result, ok ', priceInfos)
          _this.saveProductPrice(priceInfos)
        })
      })
    },
    saveProductPrice (storePrices) {
      var _this = this
      console.log('save product price ', storePrices)
      storePrices.forEach(storePrice => {
        storePrice.models.forEach(priceModel => {
          const model = _this.models.find(model => {
            return model.sku === priceModel.sku
          })
          model.update = true
          const existPriceInfo = model.price_info.find(priceInfo => {
            return priceInfo.store_id === storePrice.store_id
          })
          if (!existPriceInfo) {
            model.price_info.push({
              current_price: priceModel.current_price,
              original_price: priceModel.original_price,
              store_id: storePrice.store_id,
              discount_id: storePrice.discount.discount_id,
              currency: storePrice.currency
            })
          } else {
            existPriceInfo.current_price = priceModel.current_price
            existPriceInfo.original_price = priceModel.original_price
            existPriceInfo.discount_id = storePrice.discount.discount_id
          }
        })
      })
    }
  },
  props: ['mainSku', 'specifications', 'models', 'imageOptions'],
  comments: {
    UploadImageDialog
  }
}
</script>
