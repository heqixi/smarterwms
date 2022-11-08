<template>
  <q-card>
    <q-banner inline-actions class="text-white bg-blue-5">类别信息</q-banner>
    <q-card-section>
      <div class="row justify-begin">
        <div class="col-4">
          <q-select
            dense
            v-model="currentCategory.merchant"
            :options="merchants"
            option-label="name"
            @filter="filterFn"
            @input="switchMerchant"
            transition-show="scale"
            transition-hide="scale">
            <template v-slot:before class="q-mb-sm">
              <span :style="{color:'red', fontSize:'8px'}"> * </span>
              <div class="text-body2">
                商店
              </div>
            </template>
          </q-select>
        </div>
        <div class="col-2 q-ml-lg">
          <q-select
            dense
            v-model="categoryTemplate"
            :options="categoryTemplates"
            option-label="template_name"
            @filter="filterCategoryTemplate"
            @input="switchCategoryTemplate"
            label="快速选择类别模板"
            transition-show="scale"
            transition-hide="scale">
          </q-select>
        </div>
        <div class="col-2 q-ml-md">
          <q-btn @click="categoryTemplateNamePopup">
            保存为模板
          </q-btn>
        </div>
      </div>
      <div class="row q-mt-md justify-start">
        <div class="col-0.5">
          <div class="row">
            <span :style="{color:'red', fontSize:'8px'}"> * </span>
            <div class="text-body2">
              类别
            </div>
          </div>
        </div>
        <div class="col-4">
          <q-btn-dropdown
            ref="categoryDropdown"
            push
            flat
            auto-close
            @click="showCategoryMenu"
            :style="{width: '800px', maxWidth: '800px'}">
            <template v-slot:label>
              <span> {{categoryFullName}}</span>
            </template>
            <div class="row justify-start" :style="{width: '800px', maxWidth: '800px'}" tabindex="-1" contentEditable>
              <div class="col q-ml-xs-sm"
                   v-for="(categories, index) in categoriesLevelOptions" :key="index">
                <q-menu
                  :ref="menuRef(index)"
                  persistent
                  transition-show="scale"
                  transition-hide="scale"
                  :max-width="categoryMenuWidth(categories)"
                  max-height="400px"
                  fit>
                  <q-list>
                    <q-item clickable v-for="(category, rootIdx) in categories " :key="rootIdx"
                            @click="onCategoryClick(category, index)">
                      <q-item-section>
                        <div>{{ category.display_category_name }}</div>
                      </q-item-section>
                      <q-item-section v-if="category.has_children" avatar>
                        <q-icon color="primary" name="arrow_right" />
                      </q-item-section>
                    </q-item>
                  </q-list>
                </q-menu>
              </div>
            </div>
          </q-btn-dropdown>
        </div>
        <div class="col-2 q-ml-md">
          <q-btn @click="refreshCategory">
            刷新
          </q-btn>
        </div>
      </div>

      <div class="row justify-start q-mt-md">
        <div class="col-3 q-ml-lg q-mr-lg">
          <q-select
            dense
            v-model="currentCategory.brand_info.brand"
            :options="currentCategory.brands"
            use-input
            :option-label="brand => {return brand.display_brand_name}"
            @filter="filterBrands"
            transition-show="scale"
            transition-hide="scale"
            @input="udpateBrand">
            <template v-slot:before class="q-mb-sm">
              <span :style="{color:'red', fontSize:'8px'}"> * </span>
              <div class="text-body2">
                品牌
              </div>
            </template>
          </q-select>
        </div>
        <div
          v-for="(attr, index) in currentCategory.attributes"
          :key="index"
          class="col-3 q-ml-lg q-mr-lg">
          <div v-if="(attr.is_mandatory || expand || index < 4)">
            <q-select
              v-if="attr.type === 'select'"
              dense
              square
              v-model="attr.value"
              :multiple="attr.multiple"
              :use-input="attr.userInput"
              :clearable="attr.multiple"
              :options="attr.attribute_value_list"
              :option-label="value => {return value.display_value_name}"
              transition-show="scale"
              transition-hide="scale"
              @input="value => {updateAttribute(attr,value)}"
              @clear="value => {clearAttributeValues(attr, value)}">
              <template v-slot:before class="q-mb-sm">
                <span v-if="attr.is_mandatory" :style="{color:'red', fontSize:'8px'}"> * </span>
                <div class="text-body2">
                  {{attr.display_attribute_name}}
                </div>
              </template>
            </q-select>
            <q-input
              v-else
              dense
              v-model="attr.value.display_value_name"
              @input="value => {updateAttribute(attr, value)}">
              <template v-slot:before class="q-mb-sm">
                <span v-if="attr.require" :style="{color:'red', fontSize:'8px'}"> * </span>
                <div class="text-body2">
                  {{attr.display_attribute_name}}
                </div>
              </template>
            </q-input>
          </div>
        </div>
        <div class="full-width text-center q-mt-sm q-pa-none">
          <q-btn class="text-caption" style="width: 100px" @click="expand = !expand">
            {{ buttoText }}
          </q-btn>
        </div>
      </div>
    </q-card-section>
  </q-card>
</template>

<script>
import { getauth, postauth } from 'boot/axios_request'
import NewFormDialog from 'components/Share/newFormDialog'

const ATTRIBUTE_INPUT_TYPE = {
  DROP_DOWN: 'DROP_DOWN',
  MULTIPLE_SELECT: 'MULTIPLE_SELECT',
  TEXT_FILED: 'TEXT_FILED',
  COMBO_BOX: 'COMBO_BOX',
  MULTIPLE_SELECT_COMBO_BOX: 'MULTIPLE_SELECT_COMBO_BOX'
}

export default {
  name: 'GoodsBaseInfo',
  data () {
    return {
      expand: false,
      categoryTemplate: undefined,
      hasLoadAttributeTemplate: false,
      hasLoadAllMechant: false,
      categoryUpdate: false,
      currentMerchant: undefined,
      merchants: [],
      categoryTemplates: [],
      categoriesLevelOptions: [],
      error1: this.$t('goods.view_goodslist.error1')
    }
  },
  computed: {
    buttoText () {
      return this.expand ? '收起' : '展开'
    },
    currentCategory () {
      const emptyCategory = {
        id: undefined,
        merchant: {
          id: undefined,
          uid: undefined,
          name: undefined
        },
        merchant_id: undefined,
        category_id: undefined,
        sub_category: undefined,
        attributes: [],
        brand_info: {
          brand: {
            brand_id: 0,
            display_brand_name: 'NoBrand',
            original_brand_name: 'NoBrand'
          }
        },
        brands: undefined
      }
      if (this.category) {
        this.processCategoryAttributes(this.category, this.category.attributes, this.category.attribute_values)
      }
      return this.category || emptyCategory
    },
    categoryFullName () {
      if (!this.currentCategory || !this.currentCategory.category_id) {
        return '请选择产品类别'
      }
      let fullName = ''
      let subCategory = this.currentCategory
      while (subCategory && subCategory.category_id) {
        fullName += subCategory.display_category_name
        subCategory = subCategory.sub_category
        if (subCategory && subCategory.category_id) {
          fullName += ' > '
        }
      }
      return fullName
    }
  },
  methods: {
    categoryMenuWidth (categories) {
      const maxCharNum = categories.reduce((maxNum, category) => {
        return Math.max(maxNum, category.display_category_name.length)
      }, 0)
      return maxCharNum * 20 + 'px'
    },
    menuRef (index) {
      return 'menu' + index
    },
    showCategoryMenu () {
      var _this = this
      console.log('show category Menu')
      if (!_this.currentCategory || !_this.currentCategory.merchant) {
        this.$q.notify({
          message: '请先选择商店',
          icon: 'close',
          color: 'negative'
        })
        return
      }
      if (!_this.categoriesLevelOptions || _this.categoriesLevelOptions.length <= 0) {
        console.log('show category Menu get root')
        _this.getRootCategory(_this.currentCategory.merchant.uid).then(() => {
          setTimeout(() => {
            for (var i = 0; i < _this.categoriesLevelOptions.length; i++) {
              const ref = _this.menuRef(i)
              _this.$refs[ref][0].show()
            }
          }, 100)
        })
      } else {
        console.log('show category root length ', _this.categoriesLevelOptions.length)
        setTimeout(() => {
          for (var i = 0; i < _this.categoriesLevelOptions.length; i++) {
            const ref = _this.menuRef(i)
            _this.$refs[ref][0].show()
          }
        }, 100)
      }
    },
    hideCategoryMenu () {
      this.$refs.categoryDropdown.hide()
    },
    onCategoryClick (categoryClicked, index) {
      var _this = this
      const id = categoryClicked.id
      let categoryAtLevel = _this.currentCategory
      let i = 0
      while (i++ < index) {
        if (!categoryAtLevel.sub_category) {
          categoryAtLevel.sub_category = {}
          // _this.$set(categoryAtLevel, 'sub_category', {})
        }
        categoryAtLevel = categoryAtLevel.sub_category
      }
      if (categoryAtLevel.category_id !== categoryClicked.category_id) {
        categoryAtLevel.sub_category = undefined
        categoryAtLevel.brands = []
      }
      if (categoryAtLevel.id) {
        categoryAtLevel.update = true
      }
      categoryAtLevel.category_id = categoryClicked.category_id
      categoryAtLevel.display_category_name = categoryClicked.display_category_name
      categoryAtLevel.original_category_name = categoryClicked.original_category_name
      categoryAtLevel.has_children = categoryClicked.has_children
      _this.$set(_this.currentCategory, 'update_time', new Date().getTime()) // 为了触发更新计算属性 categoryFullName
      if (categoryClicked.has_children) {
        getauth('shopee/category/subcategory?merchant_id=1309172&id=' + id, {}).then(subCategories => {
          subCategories.forEach(category => {
            if (category.has_children) {
              category.children = []
            }
            categoryClicked.children.push(category)
          })
          const optionLevel = _this.categoriesLevelOptions.length
          if (optionLevel - 1 > index) {
            this.categoriesLevelOptions.splice(index + 1, optionLevel - index - 1, subCategories)
          } else {
            _this.categoriesLevelOptions.push(subCategories)
          }
          setTimeout(() => {
            _this.showCategoryMenu()
          }, 200)
        })
      } else {
        _this.getCategoryAttribute(_this.currentCategory.merchant.uid, categoryClicked)
        if (_this.categoryTemplate) {
          let subCategory = _this.categoryTemplate
          while (subCategory.sub_category) {
            subCategory = subCategory.sub_category
          }
          if (subCategory && subCategory.category_id !== categoryClicked.category_id) {
            _this.categoryTemplate = undefined
          }
        }
        _this.hideCategoryMenu()
      }
    },
    categoryTemplateNamePopup () {
      var _this = this
      if (!this.currentCategory || !this.currentCategory.category_id) {
        _this.$q.notify({
          message: '请先完善类别信息',
          icon: 'close',
          color: 'negative'
        })
      }
      let subCategory = this.currentCategory
      while (subCategory && subCategory.category_id) {
        subCategory = subCategory.sub_category
      }
      if (subCategory && subCategory.has_children) {
        _this.$q.notify({
          message: '请先完善类别信息',
          icon: 'close',
          color: 'negative'
        })
        return
      }
      const catetoryAttrbutes = this.currentCategory.attributes || []
      for (let i = 0; i < catetoryAttrbutes.length; i++) {
        const attribute = catetoryAttrbutes[i]
        if (attribute.is_mandatory) {
          const attrebuteValue = attribute.value
          if (!attrebuteValue || (Array.isArray(attrebuteValue) && attrebuteValue.length <= 0)) {
            console.log('missing madatory attribute value ,', attribute)
            this.$q.notify({
              message: '缺少必要的类别属性值',
              icon: 'close',
              color: 'negative'
            })
            return
          }
        }
      }
      if (_this.categoryTemplate) {
        _this.$q.notify({
          message: '无需重复保存模板',
          icon: 'check',
          color: 'green'
        })
        return
      }
      const formItems = [
        {
          name: 'template_name',
          label: '模板名称',
          type: 'text',
          edit: true,
          field: 'template_name'
        }
      ]
      const templateNameForm = {
        template_name: undefined
      }
      this.$q.dialog({
        component: NewFormDialog,
        title: '请输入模板名称',
        newFormItems: formItems,
        newFormData: templateNameForm
      }).onOk(() => {
        console.log('new category name ', templateNameForm)
        if (!templateNameForm.template_name) {
          _this.$q.notify({
            message: '请输入正确的模板名称',
            icon: 'close',
            color: 'negative'
          })
        } else {
          _this.saveAsCategoryTemplate(templateNameForm.template_name)
        }
      })
    },
    saveAsCategoryTemplate (templateName) {
      var _this = this
      const attributeValues = []
      if (this.currentCategory.attributes) {
        this.currentCategory.attributes.forEach(attribute => {
          let values
          if (Array.isArray(attribute.value)) {
            values = attribute.value
          } else {
            values = attribute.value ? [attribute.value] : []
          }
          values.forEach(value => {
            if (value.value_id) {
              attributeValues.push({
                attribute_id: attribute.attribute_id,
                display_value_name: value.display_value_name,
                value_id: value.value_id,
                multiple: attribute.multiple
              })
            }
          })
        })
      }
      let leafCategory = this.currentCategory
      while (leafCategory.sub_category) {
        leafCategory = leafCategory.sub_category
      }
      const formData = {
        merchant_id: this.currentCategory.merchant.uid,
        category_id: leafCategory.category_id,
        brand_id: this.currentCategory.brand_info.brand.brand_id,
        display_brand_name: this.currentCategory.brand_info.brand.display_brand_name,
        attributes: this.currentCategory.attributes,
        attribute_values: attributeValues,
        template_name: templateName
      }
      console.log('save category template ', formData)
      postauth('shopee/category/template', formData).then(saveTemplate => {
        console.log('save template success ', saveTemplate)
        _this.categoryTemplate = saveTemplate
        _this.categoryTemplates.push(saveTemplate)
      })
    },
    refreshCategory () {
      var _this = this
      getauth('shopee/category/refresh?merchant_id=1309172', {}).then(rootCategories => {
        rootCategories.forEach(rootCategory => {
          rootCategory.children = []
          _this.category.root.push(rootCategory)
        })
        _this.categoriesLevelOptions.push(rootCategories)
      })
    },
    getCategoryAttribute (merchantId, category) {
      const path = `shopee/category/attribute?merchant_id=${merchantId}&id=${category.category_id}&brands=true`
      var _this = this
      _this.showLoading()
      const t = setTimeout(() => {
        _this.$q.notify({
          message: '请求超时',
          icon: 'close',
          color: 'negative'
        })
        _this.hideLoading()
      }, 30 * 1000)
      getauth(path, {}).then(result => {
        console.log('get category attribute and brand', result)
        const brands = result.brands
        const attributeList = result.attributes
        // 如果之前已经存在了类别属性，因为类别已经改变，需要删除之前的类别属性
        _this.deleteCategoryAttribute(_this.currentCategory)
        _this.processCategoryAttributes(category, attributeList, [])
        _this.$set(_this.currentCategory, 'attributes', attributeList)
        _this.$set(_this.currentCategory, 'brands', brands)
        _this.hideLoading()
        clearTimeout(t)
      })
    },
    deleteCategoryAttribute (category) {
      const attributes = category.attributes
      if (!attributes) {
        return
      }
      attributes.forEach(attr => {
        if (attr.value) {
          if (!category.delete_values) {
            category.delete_values = []
          }
          if (Array.isArray(attr.value)) {
            attr.value.forEach(val => {
              if (val.id) {
                category.delete_values.push(val)
              }
            })
          } else if (attr.value.id) {
            category.delete_values.push(attr.value)
          }
        }
      })
    },
    showLoading () {
      this.$q.loading.show({
        message: '正在加载类别信息',
        boxClass: 'bg-grey-2 text-grey-9',
        spinnerColor: 'primary'
      })
    },
    hideLoading () {
      this.$q.loading.hide()
    },
    processCategoryAttributes (category, attributes, attributesValues) {
      attributes.sort((attributeA, attributeB) => {
        if (attributeA.is_mandatory && !attributeB.is_mandatory) {
          return -1
        }
        if (!attributeA.is_mandatory && attributeB.is_mandatory) {
          return 1
        }
        return attributeA.attribute_id - attributeB.attribute_id
      })
      const attributeValuesSaved = attributesValues || []
      attributes.forEach(attribute => {
        let attributeValueModel = {
          attribute_id: attribute.attribute_id,
          display_value_name: undefined,
          value_id: undefined
        }
        let attributeValueSaved = attributeValuesSaved.find(attributeValue => {
          return attributeValue.attribute_id === attribute.attribute_id
        })
        const inputType = attribute.input_type
        if (inputType === ATTRIBUTE_INPUT_TYPE.MULTIPLE_SELECT ||
          inputType === ATTRIBUTE_INPUT_TYPE.MULTIPLE_SELECT_COMBO_BOX
        ) {
          attributeValueSaved = attributeValuesSaved.filter(attributeValue => {
            return attributeValue.attribute_id === attribute.attribute_id
          })
          attribute.multiple = true
        }
        attributeValueModel = attributeValueSaved || attributeValueModel
        this.$set(attribute, 'value', attributeValueModel)
        if (inputType === ATTRIBUTE_INPUT_TYPE.MULTIPLE_SELECT ||
          inputType === ATTRIBUTE_INPUT_TYPE.COMBO_BOX ||
          inputType === ATTRIBUTE_INPUT_TYPE.MULTIPLE_SELECT_COMBO_BOX ||
          inputType === ATTRIBUTE_INPUT_TYPE.DROP_DOWN
        ) {
          attribute.type = 'select'
          attribute.multiple = inputType === ATTRIBUTE_INPUT_TYPE.MULTIPLE_SELECT || inputType === ATTRIBUTE_INPUT_TYPE.MULTIPLE_SELECT_COMBO_BOX
          attribute.userInput = inputType === ATTRIBUTE_INPUT_TYPE.COMBO_BOX || inputType === ATTRIBUTE_INPUT_TYPE.MULTIPLE_SELECT_COMBO_BOX
          attribute.options = attribute.attribute_value_list
        }
      })
    },
    switchCategoryTemplate (categoryTemplate) {
      // 默认第一个是当前的类别
      let subCategory = this.currentCategory
      while (subCategory.sub_category) {
        subCategory = subCategory.sub_category
      }

      let templateLeafCategory = categoryTemplate
      while (templateLeafCategory.sub_category) {
        templateLeafCategory = templateLeafCategory.sub_category
      }
      if (subCategory.category_id !== templateLeafCategory.category_id) {
        this.currentCategory.update = true
      }
      categoryTemplate.attribute_values.forEach(val => {
        // 因为属性值的id是模板表的id，模板属性的结构和产品类别的属性结构是一致的，在保存到特定产品的类别的时候要除去id，
        // 否则会被当成该产品的已有属性来处理
        val.id = undefined
      })
      this.currentCategory.category_id = categoryTemplate.category_id
      this.currentCategory.display_category_name = categoryTemplate.display_category_name
      this.currentCategory.original_category_name = categoryTemplate.original_category_name
      this.currentCategory.sub_category = categoryTemplate.sub_category
      this.currentCategory.attribute_values = categoryTemplate.attribute_values
      this.currentCategory.brand_info = categoryTemplate.brand_info
      this.deleteCategoryAttribute(this.currentCategory)
      this.currentCategory.attributes = categoryTemplate.attributes
      this.processCategoryAttributes(this.currentCategory, this.currentCategory.attributes, categoryTemplate.attribute_values)
      this.currentCategory.attributes.forEach(attr => {
        if (categoryTemplate.attribute_values.find(val => { return val.attribute_id === attr.attribute_id })) {
          attr.update = true
        }
      })
    },
    switchMerchant (merchant) {
      this.$emit('merchantChange', merchant)
    },
    getRootCategory (merchantId) {
      var _this = this
      return new Promise(resolve => {
        getauth('shopee/category/root?merchant_id=' + merchantId, {}).then(rootCategories => {
          rootCategories.forEach(rootCategory => {
            rootCategory.children = []
            rootCategory.lazy = true
          })
          _this.categoriesLevelOptions.push(rootCategories)
          resolve()
        })
      })
    },
    filterFn (val, update, abort) {
      var _this = this
      if (_this.hasLoadAllMechant) {
        // already loaded all mechants
        console.log('has load all merchants')
        update()
        return
      }
      getauth('store/all?type=1', {}).then(merchants => {
        _this.hasLoadAllMechant = true
        console.log('get all store ', merchants)
        update(() => {
          merchants.forEach(merchant => {
            if (!_this.merchants.find(existMerchant => { return existMerchant.uid === merchant.uid })) {
              _this.merchants.push(merchant)
            }
          })
        })
      })
    },
    filterCategoryTemplate (val, update, abort) {
      var _this = this
      if (_this.hasLoadAttributeTemplate) {
        // already loaded all mechants
        console.log('has load all merchants')
        update()
        return
      }
      if (!_this.currentCategory || !_this.currentCategory.merchant) {
        this.$q.notify({
          message: '请先选择商家',
          icon: 'close',
          color: 'negative'
        })
        update()
      }
      const merchantId = _this.currentCategory.merchant.uid
      getauth(`shopee/category/template?merchant_id=${merchantId}`, {}).then(categoryTemplates => {
        _this.hasLoadAttributeTemplate = true
        update(() => {
          _this.categoryTemplates.splice(0, _this.categoryTemplates.length)
          categoryTemplates.forEach(template => {
            _this.categoryTemplates.push(template)
          })
        })
      })
    },
    filterBrands (val, update, abort) {
      var _this = this
      if (_this.currentCategory.brands && _this.currentCategory.brands.length > 0) {
        console.log('has load all brand')
        update(() => {
          if (!val || val.length <= 0) {
            if (_this.currentCategory.allBrands) {
              _this.currentCategory.brands = _this.currentCategory.allBrands
            }
          } else {
            const filterBrands = _this.currentCategory.brands.filter(brand => {
              return brand.display_brand_name.indexOf(val) > 0
            })
            if (!_this.currentCategory.allBrands) {
              _this.currentCategory.allBrands = _this.currentCategory.brands
            }
            _this.$set(_this.currentCategory, 'brands', filterBrands)
            // _this.currentCategory.brands = filterBrands
            console.log('filter brands result ', val, filterBrands.length)
          }
        })
        return
      }
      const merchantId = _this.currentCategory.merchant.uid
      let leafCategory = _this.currentCategory
      while (leafCategory.sub_category) {
        leafCategory = leafCategory.sub_category
      }
      if (leafCategory.has_children) {
        throw new Error('Only Leaf category has brands')
      }
      console.log('begin to get brands for category ....., ', _this.currentCategory.brands)
      const t = setTimeout(() => {
        _this.$q.notify(
          {
            message: '请求超时',
            icon: 'close',
            color: 'negative'
          }
        )
        _this.loading = false
      }, 30 * 1000)
      const path = `shopee/category/brands?merchant_id=${merchantId}&id=${leafCategory.category_id}`
      getauth(path, {}).then(brands => {
        console.log('get brands for category ', leafCategory.category_id, brands)
        _this.loading = false
        clearTimeout(t)
        update(() => {
          _this.$set(_this.currentCategory, 'brands', brands)
          console.log('set brands for category success ', _this.currentCategory.brands)
        })
      })
    },
    updateAttribute (attr, value) {
      console.log('on attribute update ', value, this.currentCategory.attributes)
      attr.update = true
      this.categoryTemplate = undefined
    },
    clearAttributeValues (attr, values) {
      console.log('clear attribute value ', attr, values)
      if (Array.isArray(values)) {
        values.forEach(value => {
          if (value.id) {
            if (!attr.delete_values) {
              attr.delete_values = []
            }
            attr.delete_values.push(value)
            attr.update = true
          }
        })
      }
    },
    udpateBrand (value) {
      console.log('update brand ', this.currentCategory)
      this.currentCategory.brand_info.update = true
    }
  },
  props: ['category']
}
</script>
