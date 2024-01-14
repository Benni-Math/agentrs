// TODO: add from_string or some method of generating these cleanly in Python
pub enum Operation<'a> {
    AddToProperty(&'a str),
}
