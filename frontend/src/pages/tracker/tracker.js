import React, { useState } from "react";
import Stack from "@mui/material/Stack";
import Snackbar from "@mui/material/Snackbar";
import Button from '@mui/material/Button';
import TextField from "@mui/material/TextField";
import DataGrid, {
  Pager,
  Column,
  Editing,
  FilterRow,
  Lookup,
} from "devextreme-react/data-grid";
import { createStore } from "devextreme-aspnet-data-nojquery";
import { states } from "../../data/states";
import Box from "@mui/material/Box";

const store = createStore({
  key: "id",
  loadUrl: "/api/v1/track",
  insertUrl: "/api/v1/track/insert",
  updateUrl: "/api/v1/track/update",
  deleteUrl: "/api/v1/track/delete",
});

export default function Tracker() {
  const [integerValue, setIntegerValue] = useState('');
  const [error, setError] = useState('');
  const [openSnackbar, setOpenSnackbar] = React.useState(false);

  const handleChange = (event) => {
    const value = event.target.value;
    setIntegerValue(value);
    if (Number.isInteger(Number(value))) {
      setError('');
    } else {
      setError('Please enter a valid integer');
    }
  };


  const handleCloseSnackbar = (
    event,
    reason,
  ) => {
    if (reason === 'clickaway') {
      return;
    }

    setOpenSnackbar(false);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!error && integerValue !== '') {
      console.log('Submitted integer:', integerValue);
      try {
        const response = await fetch('/api/v1/track/add', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ value: parseInt(integerValue, 10) }),
        });

        if (response.ok) {
          setIntegerValue('');
          setOpenSnackbar(true);
        } else {
          throw new Error('Server responded with an error');
        }
      } catch (error) {
        console.error('Submission error:', error);
        setError('Error submitting form. Please try again.');
      }
    }
  };

  return (
    <>
      <Snackbar
        open={openSnackbar}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        message="ID will be tracked at next crawler run"
      />
      <Stack>
        <form onSubmit={handleSubmit}>
          <Box sx={{ display: 'flex', alignItems: 'center', m: 2, mb: 0 }} spacing={2}>
            <TextField
              fullWidth
              label="Add new themoviedb tv show id"
              variant="outlined"
              value={integerValue}
              onChange={handleChange}
              error={error != ''}
              helperText={error}
              sx={{ mb: 2 }}
            />
            <Button
              sx={{ ml: 1, mt: -2 }}
              type="submit"
              variant="contained"
              color="primary"
              disabled={error || integerValue === ''}
            >
              Add
            </Button>
          </Box>
        </form>


        <Box sx={{ m: 2 }}>
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
            <Column dataField="season" caption="Season" dataType="number" />
            <Column dataField="date" caption="Date" dataType="date" format="yyyy-MM-dd" />
            <Column
              dataField="state"
              caption="State"
              dataType="string"
              filterValue="New"
            >
              <Lookup dataSource={states} valueExpr="ID" displayExpr="Name" />
            </Column>
          </DataGrid>
        </Box>
      </Stack>
    </>
  );
}
