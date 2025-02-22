use axum::{http::{request, StatusCode}, response::IntoResponse, Json};
use serde::{Deserialize, Serialize};

pub async fn process_data(Json(request): Json<DataRequest>) -> impl IntoResponse {
    // Calculate sums and return response
    let mut int_count: i32 = 0;
    let mut string_length_count: i32 = 0;

    for some_value in &request.data
    {
        match some_value
        {
            StringOrInt::Num(number) => int_count += number,
            StringOrInt::Message(message) => string_length_count += message.chars().count() as i32
        }
    }

    let response = DataResponse {
        string_len: string_length_count, int_sum: int_count
    };
    (StatusCode::OK, Json(response))
}

#[derive(Deserialize)]
#[serde(untagged)]
pub enum StringOrInt{
    Message(String),
    Num(i32)
}

#[derive(Deserialize)]
pub struct DataRequest {
    data: Vec<StringOrInt>
}


#[derive(Serialize)]
pub struct DataResponse {
    string_len: i32,
    int_sum: i32
}
