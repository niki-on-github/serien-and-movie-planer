import React from "react";
import DataGrid, {
  Pager,
  Column,
  Editing,
  FilterRow,
  Lookup,
} from "devextreme-react/data-grid";
import { createStore } from 'devextreme-aspnet-data-nojquery';
import { states } from '../../data/states'

const store = createStore({
    key: "id",
    loadUrl: "/v1/movies",
    insertUrl: "/v1/movies/insert",
    updateUrl: "/v1/movies/update",
    deleteUrl: "/v1/movies/delete"
});

export default function Movies() {
  return (
    <>
      <h2 className={"content-block"}>Movies</h2>

      <DataGrid
        dataSource={store}
        showBorders={true}
        columnAutoWidth={true}
        columnHidingEnabled={true}
      >
        <Pager showPageSizeSelector={true} showInfo={true} />
        <FilterRow visible={true} />
        <Editing
          mode="cell"
          allowUpdating={true}
          allowAdding={false}
          allowDeleting={false}
        />
        <Column dataField="title" caption="Title" dataType="string" />
        <Column dataField="longTitle" caption="Long Title" dataType="string" />
        <Column dataField="date" caption="Date" dataType="date" />
        <Column dataField="state" caption="State" dataType="string" filterValue="New">
          <Lookup dataSource={states} valueExpr="ID" displayExpr="Name" />
        </Column>
      </DataGrid>
    </>
  );
}
