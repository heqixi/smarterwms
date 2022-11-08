<template>
  <q-table
      class="my-sticky-header-table shadow-24"
      :data="table_list"
      :row-key="rowKey"
      :separator="separator"
      :loading="loading"
      :filter="filter"
      :columns="columns"
      :pagination="pagination"
      :selection="multipleSelect ? 'multiple' : 'single'"
      :selected.sync="selected"
      :filter-method="customFilter"
      :rows-per-page-label="rowPerPageLabel"
      :table-style="{ height: height || tableHeight, width: tableWidth || '100%'}"
      :style="tableStyle"
      no-data-label="No data"
      no-results-label="No data you want"
      flat
      bordered
      dense
      virtual-scroll
      :virtual-scroll-slice-size="15">
      <template v-slot:top>
        <q-btn-group push>
          <!--        <q-btn :label="$t('new')" icon="add" @click="$emit('newForm')">-->
          <!--          <q-tooltip-->
          <!--            content-class="bg-amber text-black shadow-4"-->
          <!--            :offset="[10, 10]"-->
          <!--            content-style="font-size: 12px"-->
          <!--          >{{ $t('newtip') }}-->
          <!--          </q-tooltip-->
          <!--          >-->
          <!--        </q-btn>-->
          <q-btn :label="$t('refresh')" icon="refresh" @click="refresh">
            <q-tooltip
              content-class="bg-amber text-black shadow-4"
              :offset="[10, 10]"
              content-style="font-size: 12px"
            >{{ $t('refreshtip') }}
            </q-tooltip
            >
          </q-btn>
          <q-btn
            v-for="(action, index) in topButtons"
            :key="index"
            :label="action.label"
            :icon="action.icon"
            @click="onSelect(action)">
            <q-tooltip
              content-class="bg-amber text-black shadow-4"
              :offset="[10, 10]"
              content-style="font-size: 12px"
            >{{ action.tip }}
            </q-tooltip
            >
          </q-btn>
        </q-btn-group>
        <q-space/>
        <q-input
          v-if="!hideSearch"
          outlined
          rounded
          dense
          debounce="300"
          color="primary"
          v-model="search"
          :placeholder="$t('search')"
          @focusin="searchFoucs"
          @click="searchClick">
          <template v-slot:append>
            <q-icon name="search"/>
          </template>
        </q-input>
      </template>

      <!--表头-->
      <template v-slot:header="props">
        <q-tr v-show="!loading">
          <q-th class="col" style="width:60px">
            <q-checkbox dense v-model="props.selected"/>
          </q-th>
          <q-th
            v-for="col in props.cols"
            :key="col.name"
            :props="props"
            :style="col.style">
            <q-tr v-if="col.type === 'table'" class="row justify-between">
              <div
                style="border-right: 1px solid rgba(0,0,0, 0.12)"
                v-for="(subCol, subColIdx) in col.subColumns" :key="subColIdx"
                :class="subCol.class"
              >
                <tr v-if="subCol.type === 'table'" class="row">
                  <div v-for="(leafCol, leafColIdx) in subCol.subColumns" :key="leafColIdx"
                       :class="leafCol.class"
                       style="border-right: 1px solid rgba(0,0,0, 0.12)">
                    {{ leafCol.label }}
                  </div>
                </tr>
                <div v-else>
                  {{ subCol.label }}
                </div>
              </div>
            </q-tr>
            <div v-else>
              {{ col.label }}
            </div>
          </q-th>
        </q-tr>
      </template>
      <template v-slot:body="props">
        <q-tr :props="props">
          <q-td>
            <q-checkbox dense class="absolute-center" v-model="props.selected"/>
          </q-td>
          <td v-for="col in columns" :key="col.name" :style="col.style">
            <div v-if="col.type === 'image'">
              <q-img
                :src="_getFieldValue(props.row, col)"
                spinner-color="white"
                style="max-width: 100px; max-height: 100px;"
                img-class="my-custom-image"
                class="rounded-borders test"
                @click="zoomThisImage(props.row, col)"
              />
            </div>
            <div
              v-else-if="col.type === 'select'"
              @click="onFieldOfRowClick(props.row, col)">
              <q-select
                v-if="col.name === editColName && props.row[rowKey] === editRowKey"
                filled
                v-model="editValue"
                :options="col.globalOptions ? col.globalOptions : props.row[col.options]"
                :option-label="col.optionLabel"
                :multiple="col.multiple"
                use-input
                :hint="col.hint"
                @filter="col.filterFn"
                @input="col.onInput"
                @keydown.enter="_onFieldUpdated(props.row, col)"
                @blur="onFieldOfRowBlur()"
                clearable
                dense>
                <template v-if="col.newValue" v-slot:append>
                  <q-btn
                    round
                    dense
                    flat
                    icon="add"
                    @click.stop="col.newValue(props.row).then(newValue => {setEditValue(newValue, col.multiple);})"
                  />
                </template>
              </q-select>
              <div v-else>
                {{ _getOptionLabel(props.row, col) }}
              </div>
            </div>
            <div v-else-if="col.type === 'table'">
              <div class="relative-position">
                <div v-show="!(loadingRow === props.row[rowKey] && loadingCol === col.name)">
                  <q-list class="q-pa-none">
                    <q-item class="q-pa-none" v-for="(subRow, rowIndex) in _getFieldValue(props.row, col)" :key="rowIndex">
                      <div class="full-width row">
                        <div
                          style="border-left: 1px solid rgba(0,0,0, 0.12);border-right: 1px solid rgba(0,0,0, 0.12); border-top: 1px solid rgba(0,0,0, 0.12); border-bottom: 1px solid rgba(0,0,0, 0.12); display: table; align-items: center; word-break: break-word;"
                          v-for="subCol in col.subColumns"
                          :key="Math.ceil(Math.random() * 10000) +'_' + col.name +'_' +subCol.name"
                          :class="subCol.class">
                          <div v-if="subCol.type === 'image'">
                            <div>
                              <q-img
                                :src="_getFieldValue(subRow, subCol)"
                                spinner-color="white"
                                :style="subCol.imageStyle"
                                img-class="my-custom-image"
                                class="rounded-borders"
                                @click="zoomThisImage(subRow, subCol)"
                              />
                            </div>
                          </div>
                          <div v-else-if="subCol.type === 'select'">
                            <q-select
                              filled
                              :value="_getFieldValue(subRow, subCol)"
                              :options="subCol.globalOptions"
                              :option-label="subCol.optionLabel"
                              :multiple="subCol.multiple"
                              :hint="col.hint"
                              @keydown.enter="_onSubFieldUpdated(props.row, subRow, subCol)"
                              dense flat>
                              <template v-if="col.newValue" v-slot:append>
                                <q-btn
                                  round
                                  dense
                                  flat
                                  icon="add"
                                  @click.stop="col.newValue(props.row).then(newValue => {setEditValue(newValue, col.multiple);})"
                                />
                              </template>
                            </q-select>
                          </div>
                          <div v-else-if="subCol.type === 'url'" style="display: table-cell; vertical-align: middle; text-align: center">
                            <a :href="_getFieldValue(subRow, subCol)" target="_blank">访问</a>
                          </div>
                          <div v-else-if="subCol.type === 'actions'" style="display: table-cell; vertical-align: middle; margin: 0 auto;">
                            <q-btn-group push>
                              <q-btn
                                v-for="(action, index) in subCol.actions"
                                :key="index"
                                :label="action.label"
                                @click="action.click(props.row, subRow)">
                                <q-tooltip
                                  content-class="bg-amber text-black shadow-4"
                                  :offset="[10, 10]"
                                  content-style="font-size: 12px">{{ action.tip }}
                                </q-tooltip>
                              </q-btn>
                            </q-btn-group>
                          </div>
                          <div v-else-if="subCol.type === 'table'" class="full-width">
                            <div v-show="!(loadingRow === props.row[rowKey] && loadingCol === col.name)">
                              <q-list class="q-pa-none full-width">
                                <q-item class="q-pa-none full-width" v-for="(leafRow, rowIndex) in _getFieldValue(subRow, subCol)"
                                        :key="rowIndex">
                                  <div class="full-width row" style="width: 100%">
                                    <div
                                      style="border-right: 1px solid rgba(0,0,0, 0.12); border-bottom: 1px solid rgba(0,0,0, 0.12); display: table; word-break: break-word;"
                                      v-for="leafCol in subCol.subColumns"
                                      :key="Math.ceil(Math.random() * 10000) +'_' + col.name +'_' +subCol.name + '_' + leafCol.name"
                                      :class="leafCol.class">
                                      <div v-if="leafCol.type === 'image'">
                                        <div>
                                          <q-img
                                            :src="_getFieldValue(leafRow, leafCol)"
                                            spinner-color="white"
                                            :style="leafCol.imageStyle"
                                            img-class="my-custom-image"
                                            class="rounded-borders"
                                            @click="zoomThisImage(leafRow, leafCol)"
                                          />
                                        </div>
                                      </div>
                                      <div v-else-if="leafCol.type === 'url'">
                                        <a :href="_getFieldValue(leafRow, leafCol)" target="_blank">访问</a>
                                      </div>
                                      <div v-else-if="leafCol.type === 'actions'">
                                        <q-btn-group push>
                                          <q-btn
                                            v-for="(action, index) in leafCol.actions"
                                            :key="index"
                                            :label="action.label"
                                            @click="action.click(props.row, subRow, leafRow)">
                                            <q-tooltip
                                              content-class="bg-amber text-black shadow-4"
                                              :offset="[10, 10]"
                                              content-style="font-size: 12px">{{ action.tip }}
                                            </q-tooltip>
                                          </q-btn>
                                        </q-btn-group>
                                      </div>
                                      <div v-else :style="{ textAlign: 'center', whiteSpace: 'normal'}" style="display: table-cell; vertical-align: middle">
                                        <div v-if="leafCol.edit">
                                          <q-input
                                            style="display: inline-block"
                                            class="text-center items-center"
                                            dense
                                            flat
                                            filled
                                            hide-bottom-space
                                            borderless
                                            :value="_getFieldValue(leafRow, leafCol)"
                                            @input="(value) => _onLeafFieldModelUpdated(value)"
                                            @blur="_onLeafFieldUpdated(props.row, subRow, leafRow, leafCol)"
                                          />
                                        </div>
                                        <div v-else>
                                          {{ _getFieldValue(leafRow, leafCol) }}
                                        </div>
                                      </div>
                                    </div>
                                  </div>
                                </q-item>
                              </q-list>
                            </div>
                          </div>
                          <div v-else :style="{ textAlign: 'center', whiteSpace: 'normal'}" style="display: table-cell; vertical-align: middle" >
                            <div v-if="subCol.edit" :style="subCol.style">
                              <q-input
                                style="display: inline-block"
                                class="text-center items-center"
                                dense
                                flat
                                filled
                                hide-bottom-space
                                borderless
                                :value="_getFieldValue(subRow, subCol)"
                                @input="(value) => _onSubFieldModelUpdated(props.row, subRow, subCol, value)"
                                @blur="_onSubFieldUpdated(props.row, subRow, subCol)"
                              />
                            </div>
                            <div v-else class="full-width">
                              {{ _getFieldValue(subRow, subCol) }}
                            </div>
                          </div>
                        </div>
                      </div>
                    </q-item>
                  </q-list>
                  <div class="text-center row">
                    <div class="col" @click="toggleHeight(props.row, col)">
                      <div v-if="_getFieldValue(props.row, col).length > 0">
                        <div v-if="!col.keepExpand">
                          <span v-if="expandRow === props.row[rowKey] && expandCol === col.name">收起</span>
                          <span v-else>展开</span>
                        </div>
                      </div>
                      <div v-else>
                        <div v-if="col.nodata" @click="col.nodata.click(props.row)">
                          {{col.nodata.hint}}
                        </div>
                        <div v-else>
                          无数据
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <q-inner-loading :showing="loadingRow === props.row[rowKey] && loadingCol === col.name ">
                  <q-spinner-gears
                    size="80px"
                    color="primary"
                    label="数据加载中"
                    transition-hide="fade"
                  />
                </q-inner-loading>
              </div>
            </div>
            <div
              v-else-if="col.type === 'text' ||col.type === 'longText' || col.type === 'number'"
              class="text-center">
              <div v-if="col.edit" :style="col.style">
                <q-input
                  dense
                  filled
                  flat
                  :value="_getFieldValue(props.row, col)"
                  :type="col.type"
                  @input="(value) => _onFieldModelInput(props.row, col, value)"
                  @blur="_onFieldUpdated(props.row, col)"
                />
              </div>
              <div v-else>
                {{ _getFieldValue(props.row, col) }}
              </div>
            </div>
            <div v-else-if="col.type === 'url'">
              <a :href="_getFieldValue(props.row, col)" target="_blank">{{col.labelMap ? _getLabelValue(props.row, col): '访问'}}</a>
            </div>
            <div v-else-if="col.type === 'actions'">
              <q-btn-group push>
                <div v-for="(action, index) in col.actions" :key="index">
                  <q-btn-dropdown v-if="action.type === 'button-dropdown'" flat dense :label="action.label" @click="action.click(props.row)">
                    <q-list>
                      <q-item v-for="(subBtn, subBtnIndex) in action.subButtons" :key="subBtnIndex"
                              clickable v-close-popup @click="subBtn.click(props.row)">
                        <q-item-section>
                          <q-item-label>{{subBtn.label}}</q-item-label>
                        </q-item-section>
                      </q-item>
                    </q-list>
                  </q-btn-dropdown>
                  <q-btn
                    v-else
                    flat
                    dense
                    :label="action.label"
                    @click="action.click(props.row)">
                    <q-tooltip
                      content-class="bg-amber text-black shadow-4"
                      :offset="[10, 10]"
                      content-style="font-size: 12px">
                      {{ action.tip }}
                    </q-tooltip>
                  </q-btn>
                </div>
              </q-btn-group>
            </div>
          </td>
        </q-tr>
      </template>
      <template v-slot:loading>
        <q-inner-loading :showing="loading">
          <q-spinner-gears size="100px" color="primary"/>
        </q-inner-loading>
      </template>

      <template v-slot:pagination="scope" ref="pagination">
        <div>
                <span>
                    第 {{ (dynamicPagination.page - 1) * dynamicPagination.rowsPerPage }}
                    到
                    {{ Math.min(dynamicPagination.page * dynamicPagination.rowsPerPage, table_list.length) }}
                    条记录,共
                    {{ numRows }}
                    条记录, 已加载 {{ table_list.length }} 条数据
                </span>
          <q-btn
            icon="first_page"
            color="grey-8"
            round
            dense
            flat
            :disable="scope.isFirstPage"
            @click="fistPage(scope)"
          />

          <q-btn
            icon="chevron_left"
            color="grey-8"
            round
            dense
            flat
            :disable="scope.isFirstPage"
            @click="prePage(scope)"
          />

          <q-btn
            ref="nextPageBtn"
            icon="chevron_right"
            color="grey-8"
            round
            dense
            flat
            @click="nextPage(scope)"
          />

          <q-btn
            icon="last_page"
            color="grey-8"
            round
            dense
            flat
            @click="lastPage(scope)"
          />
        </div>
      </template>
    </q-table>

</template>

<script>
import ZoomImage from './zoomimage.vue'

export default {
  name: 'CommonTable',
  data () {
    var _this = this
    return {
      selected: [],
      separator: 'cell',
      dynamicPagination: {
        page: 1,
        rowsPerPage: 20
      },
      search_history: new Map(),
      searching: false,
      currentPage: 1,
      editRowKey: '',
      editColName: '',
      editValue: undefined,
      editSubRowKey: '',
      editSubColName: '',
      editSubValue: undefined,
      editLeafValue: undefined,
      expandRow: '',
      expandCol: '',
      textFieldWidth: '200px',
      longTextFieldWidth: '300px',
      rowPerPageLabel: '每页数量',
      loadingRow: '',
      loadingCol: '',
      defaultImage: 'http://127.0.0.1:8008/media/uploads/009.webp',
      // loading: false,
      search: '',
      pagination: {
        page: 1,
        rowsPerPage: _this.rowsPerPage || 20
      },
      editid: 0,
      heightPerRow: 30,
      editMode: false,
      height: undefined,
      innerColumns: [
        {
          name: 'sku',
          field: 'sku'
        },
        {
          name: 'price',
          field: 'price'
        }
      ]
    }
  },
  watch: {
    numRows: function (val) {
      console.log('num Rows change ')
      this.pagination.rowsNumber = val
    },
    testDynamicPag: function (val) {
      //
    }
  },
  computed: {
    filter () {
      return this.search
    }
  },
  methods: {
    searchClick (evt) {
      console.log('search click')
      evt.stopPropagation()
    },
    searchFoucs (evt) {
      console.log('search foucs')
      evt.stopPropagation()
    },
    onSelect (action) {
      var _this = this
      const promise = action.click(this.selected)
      if (promise) {
        promise.then(res => {
          if (action.selectAutoClear) {
            _this.clearSelect()
          }
        })
      }
    },
    clearSelect () {
      this.selected.splice(0, this.selected.length)
    },
    addSelected (rowKeys) {
      var _this = this
      _this.table_list.forEach(item => {
        const exist = _this.selected.find(selectItem => { return selectItem[_this.rowKey] === item[_this.rowKey ]})
        if (!exist && rowKeys.find(key => { return key === item[_this.rowKey] })) {
          _this.selected.push(item)
        }
      })
    },
    zoomThisImage (row, col) {
      const _this = this
      const imageUrl = _this._getFieldValue(row, col)
      _this.$q.dialog({
        component: ZoomImage,
        parent: _this,
        img_url: imageUrl
      })
    },
    setEditValue (newValue, multiple) {
      if (multiple) {
        this.editValue.push(newValue)
      } else {
        this.editValue = newValue
      }
    },
    _getOptionLabel (item, column) {
      let targetField = item
      if (column.field !== 'self') {
        targetField = item[column.field]
      }
      if (column.type === 'select' && column.multiple) {
        console.log('_getOptionLabel multiple select')
        if (targetField === undefined || targetField.length <= 0) {
          return '请输入'
        }
        return targetField
          .map(tag => {
            return column.optionLabel(tag)
          })
          .join(',')
      }
      if (column.type === 'select' && column.optionLabel) {
        return column.optionLabel(targetField)
      }
    },
    _getFieldValue (item, column) {
      let targetField = item
      if (column.field !== 'self') {
        targetField = item[column.field]
      }
      // if (targetField === undefined) {
      //   console.log('_getFieldValue return undifined ', item, column)
      // }
      return column.fieldMap ? column.fieldMap(targetField) : targetField
    },
    _getLabelValue (item, column) {
      let targetField = item
      if (column.field !== 'self') {
        targetField = item[column.field]
      }
      // if (targetField === undefined) {
      //   console.log('_getFieldValue return undifined ', item, column)
      // }
      return column.labelMap ? column.labelMap(targetField) : targetField
    },
    onFieldOfRowClick (row, col) {
      this.editValue = this._getFieldValue(row, col)
      this.editColName = col.name
      this.editRowKey = row[this.rowKey]
    },
    onSubFieldOfRowClick (row, col, subCol) {
      this.editSubValue = this._getFieldValue(row, subCol)
      this.editSubColName = subCol.name
      this.editSubRowKey = row[col.rowKey]
      console.log('onSubFieldOfRowClick ', row, this.editSubColName, this.editSubRowKey, col.name === this.editSubColName && row[col.rowKey] === this.editSubRowKey)
    },
    onFieldOfRowBlur () {
      this.editColName = ''
      this.editRowKey = ''
      this.editValue = undefined
    },
    _onSubFieldModelUpdated (row, subRow, subCol, newVale) {
      console.log('sub col model value update ', newVale)
      this.editSubValue = newVale
    },
    _onLeafFieldModelUpdated (newVale) {
      console.log('sub col model value update ', newVale)
      this.editLeafValue = newVale
    },
    _onLeafFieldUpdated (row, subRow, leafRow, leafCol) {
      console.log('leaf col model value update ', leafRow)
      var _this = this
      if (_this.editLeafValue === undefined) {
        console.log('edit sub value is undefined')
        return
      }
      console.log('_onLeafFieldUpdated ', leafRow, ',col ', leafCol)
      if (leafCol.onUpdate !== undefined) {
        leafCol.onUpdate(row, subRow, leafRow, _this.editLeafValue).then(newValue => {
          console.log('common table receive new update data', newValue)
          if (leafCol.setter) {
            console.log('_onSubFieldUpdated, setter ')
            leafCol.setter(leafRow, newValue)
          } else {
            _this.$set(leafRow, leafCol.field, newValue)
          }
        }).finally(() => {
          this.editSubColName = ''
          this.editSubRowKey = ''
          this.editSubValue = undefined
        })
      } else {
        if (leafCol.setter) {
          console.log('_onSubFieldUpdated, setter ')
          leafCol.setter(leafRow, _this.editSubValue)
        } else {
          leafRow[leafCol.field] = _this.editSubValue
        }
        this.editSubColName = ''
        this.editSubRowKey = ''
        this.editLeafValue = undefined
      }
    },
    _onSubFieldUpdated (row, subRow, subCol) {
      var _this = this
      if (_this.editSubValue === undefined) {
        console.log('edit sub value is undefined ')
        return
      }
      console.log('_onSubFieldUpdated ', row, ',col ', subCol)
      if (subCol.onUpdate !== undefined) {
        subCol.onUpdate(row, subRow, _this.editSubValue).then(newValue => {
          console.log('common table receive new update data', newValue)
          if (subCol.setter) {
            console.log('_onSubFieldUpdated, setter ')
            subCol.setter(subRow, newValue)
          } else {
            _this.$set(subRow, subCol.field, newValue)
            // subRow[subCol.field] = newValue
          }
        }).finally(() => {
          this.editSubColName = ''
          this.editSubRowKey = ''
          this.editSubValue = undefined
        })
      } else {
        if (subCol.setter) {
          console.log('_onSubFieldUpdated, setter ')
          subCol.setter(subRow, _this.editSubValue)
        } else {
          subRow[subCol.field] = _this.editSubValue
        }
        this.editSubColName = ''
        this.editSubRowKey = ''
        this.editSubValue = undefined
      }
    },
    _onFieldModelInput (row, col, value) {
      this.editValue = value
    },
    _onFieldUpdated (row, col) {
      var _this = this
      if (_this.editValue === undefined) {
        console.log('on field update value is undefined')
        return
      }
      console.log('_onFieldUpdated ', row, ',value', _this.editValue)
      if (col.onUpdate !== undefined) {
        col.onUpdate(row, _this.editValue).then(newValue => {
          console.log('common table receive new update data', newValue)
          if (col.setter) {
            console.log('_onFieldUpdated, setter ')
            col.setter(row[col], newValue)
          } else {
            row[col.field] = newValue
          }
        }).catch(err => {
          console.log('common table fail to update filed ', err, row, col, _this.editValue)
        }).finally(() => {
          this.editColName = ''
          this.editRowKey = ''
          this.editValue = undefined
        })
      } else {
        if (col.setter) {
          console.log('_onFieldUpdated, setter ')
          col.setter(row, _this.editValue)
        } else {
          row[col.field] = _this.editValue
        }
        this.editColName = ''
        this.editRowKey = ''
        this.editValue = undefined
      }
    },
    getSubTableHeight (row, col) {
      const expand = col.keepExpand ||
        (this.expandRow === row[this.rowKey] && this.expandCol === col.name)
      const numRows = this._getFieldValue(row, col).length
      const defaultRows = Math.min(numRows, 3)
      const unExpandHeight = defaultRows * col.rowHeight + 'px'
      if (!expand) {
        return {
          maxHeight: unExpandHeight,
          height: unExpandHeight
        }
      }
      const rowHeight = col.rowHeight ? col.rowHeight : this.heightPerRow
      const expandRowHeight = numRows * rowHeight + 'px'
      return {
        maxHeight: expandRowHeight,
        height: expandRowHeight
      }
    },
    toggleHeight (row, col) {
      var _this = this
      const expanding =
        row[_this.rowKey] === this.expandRow && this.expandCol === col.name
      if (expanding) {
        console.log('expanding , now colapse ')
        _this.expandCol = ''
        _this.expandRow = ''
        _this.loadingRow = ''
        _this.loadingCol = ''
        return
      }
      if (col.request) {
        _this.loadingRow = row[_this.rowKey]
        _this.loadingCol = col.name
        console.log('toggleHeight request data visible,', row.loading)
        col
          .request(row)
          .then(res => {
            console.log('toggleHeight request data res,', row.loading)
            _this.expandCol = expanding ? '' : col.name
            _this.expandRow = expanding ? '' : row[_this.rowKey]
            _this.loadingRow = ''
            _this.loadingCol = ''
          })
          .catch(err => {
            console.log('toggleHeight request data error ', err)
            _this.expandCol = ''
            _this.expandRow = ''
            _this.loadingRow = ''
            _this.loadingCol = ''
          })
      } else {
        _this.expandCol = col.name
        _this.expandRow = row[_this.rowKey]
        _this.loadingRow = ''
        _this.loadingCol = ''
      }
    },
    refresh () {
      this.search = ''
      this.search_history = new Map()
      this.searching = false
      this.selected = []
      this.$emit('refresh')
    },
    customFilter (rows, terms) {
      // rows contain the entire data
      // terms contains whatever you have as filter
      // lowerSearch = terms
      var _this = this
      console.log('filter before length', _this.table_list.length)
      let lowerSearch = terms
      if (lowerSearch.indexOf('搜索结果:') >= 0) {
        lowerSearch = lowerSearch.substring(5, lowerSearch.length)
      }
      let filteredRows = rows
      console.log('search term ', terms, lowerSearch)
      if (_this.search_history.get(lowerSearch) !== undefined) {
        const cached = _this.search_history.get(lowerSearch)
        return filteredRows.filter(row => { // 为了防止缓存中的搜索结果和列表不一样，统一采用列表的搜索结果，只是用id匹配
          return cached.find(cachedRow => { return cachedRow.id === row.id }) !== undefined
        })
      }
      if (_this.filterFn) {
        if (_this.searchFn && _this.search_history.get(lowerSearch) === undefined && !_this.searching) {
          _this.searching = true
          _this.searchFn(lowerSearch).then((res) => {
            _this.searching = false
            _this.search_history.set(lowerSearch, res)
            _this.search = '搜索结果:' + lowerSearch // 重新触发过滤
            console.log('get seach list success, data length', _this.table_list.length)
          }).catch(err => {
            _this.search = '搜索结果:' + lowerSearch // 重新触发过滤
            _this.searching = false
            console.log('error, applier filter fn ', err)
            filteredRows = rows.filter(row => {
              return this.filterFn(row, lowerSearch)
            })
            _this.search_history.set(lowerSearch, filteredRows)
          })
        } else {
          filteredRows = rows.filter(row => {
            return this.filterFn(row, lowerSearch)
          })
        }
      }
      console.log('custom filter terms ', terms, ',result ', filteredRows)
      return filteredRows
    },
    nextPage (scope) {
      var _this = this
      const rowsPerPage = scope.pagination.rowsPerPage
      const secondLastPage = this.table_list.length - (scope.pagination.page * rowsPerPage) < rowsPerPage
      console.log('stock list on next Page', this.numRows, this.table_list.length, secondLastPage)
      if (this.table_list.length < this.numRows && secondLastPage) {
        // 如果是倒数第二页，并且还有数据,就请求数据
        console.log('get more data')
        _this.getNextPage().then(res => {
          this.dynamicPagination.page += 1
          this.dynamicPagination.rowsPerPage = scope.pagination.rowsPerPage
          console.log('get more data success next page ')
          scope.nextPage()
        })
      } else if (!scope.isLastPage) {
        this.dynamicPagination.page += 1
        this.dynamicPagination.rowsPerPage = scope.pagination.rowsPerPage
        console.log('next page ', this.dynamicPagination)
        scope.nextPage()
      } else {
        this.$q.notify({
          message: '数据加载完毕，已是最后一页数据',
          icon: 'check',
          color: 'green'
        })
      }
    },
    prePage (scope) {
      console.log('pre page ', scope)
      this.dynamicPagination.page -= 1
      this.dynamicPagination.rowsPerPage = scope.pagination.rowsPerPage
      console.log('pre page ', this.dynamicPagination)
      scope.prevPage()
    },
    fistPage (scope) {
      console.log('first page ', scope)
      this.dynamicPagination.page = 1
      this.dynamicPagination.rowsPerPage = scope.pagination.rowsPerPage
      scope.firstPage()
    },
    lastPage (scope) {
      console.log('last page ', scope)
      var _this = this
      const size = this.numRows - this.table_list.length
      if (size > 0) {
        _this.getNextPage(size).then(res => {
          scope.lastPage()
          this.dynamicPagination.page = scope.pagesNumber
          this.dynamicPagination.rowsPerPage = scope.pagination.rowsPerPage
        })
      } else {
        this.dynamicPagination.page = scope.pagesNumber
        this.dynamicPagination.rowsPerPage = scope.pagination.rowsPerPage
        scope.lastPage()
      }
    },
    detectZoom () {
      var ratio = 0, screen = window.screen, ua = navigator.userAgent.toLowerCase()
      if (window.devicePixelRatio !== undefined) {
        ratio = window.devicePixelRatio
      } else if (~ua.indexOf('msie')) {
        if (screen.deviceXDPI && screen.logicalXDPI) {
          ratio = screen.deviceXDPI / screen.logicalXDPI
        }
      } else if (window.outerWidth !== undefined && window.innerWidth !== undefined) {
        ratio = window.outerWidth / window.innerWidth
      }
      if (ratio) {
        ratio = Math.round(ratio * 100)
      }
      // ratio 就是获取到的百分比
      console.log(ratio)
      this.onresize_height = ratio
      return ratio
    },
    resize () {
      const _this = this
      let ratio = 0
      if (_this.curWindowRatio) {
        ratio = _this.detectZoom() - _this.curWindowRatio
      }
      _this.curWindowRatio = _this.detectZoom()
      const height = (_this.$q.screen.height - 250) * ((100 - ratio) / 100)
      if (_this.$q.platform.is.electron) {
        _this.height = String(height) + 'px'
      } else {
        _this.height = height + '' + 'px'
      }
    }
  },
  mounted () {
    var _this = this
    // if (_this.$q.platform.is.electron) {
    //   _this.height = String(_this.$q.screen.height - 290) + 'px'
    // } else {
    //   _this.height = _this.$q.screen.height - 290 + '' + 'px'
    // }
    if (!_this.tableHeight) {
      window.addEventListener('resize', _this.resize, true)
      _this.resize()
    }
  },
  props: [
    'table_list',
    'rowKey',
    'topButtons',
    'numRows',
    'columns',
    'getNextPage',
    'filterFn',
    'searchFn',
    'loading',
    'preSearch',
    'tableStyle',
    'defaultSelected',
    'multipleSelect',
    'tableCells',
    'rowsPerPage',
    'hideSearch',
    'tableHeight',
    'tableWidth'
  ],
  components: {
    ZoomImage
  },
}
</script>
<style>
.sub-row-cell {
  border-left-width: 1px !important;
  padding-left: 0;
  padding-right: 0;
}
</style>
